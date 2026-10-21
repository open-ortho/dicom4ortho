"""Independently check synthetic Swift outputs, not DICOMKit self-roundtrips.

Requires pydicom>=3, numpy, Pillow, pylibjpeg, pylibjpeg-libjpeg, pylibjpeg-openjpeg,
pyjpegls, and libjxl's djxl on PATH. These are validation tools, not Swift or
Python runtime dependencies. Run dciodvfy separately for IOD validation.
"""

import argparse
from io import BytesIO
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np
import pydicom
from pydicom.encaps import generate_frames
from PIL import Image


# Independent expected standard UIDs intentionally do not reuse the implementation's
# registry. Otherwise an incorrect backend mapping could agree with its own oracle.
ENCODINGS = {
    "explicit-le": ".1", "implicit-le": "", "jpeg-baseline": ".4.50",
    "jpeg-lossless": ".4.70", "jpeg-ls-lossless": ".4.80",
    "jpeg2000-lossless": ".4.90", "jpeg2000-lossy": ".4.91",
    "htj2k-lossless": ".4.201", "htj2k-rpcl": ".4.202", "htj2k-lossy": ".4.203",
    "jpeg-xl-lossless": ".4.110", "jpeg-xl-lossy": ".4.112", "rle": ".5",
}


def validate(directory: Path) -> list[dict]:
    """Decode each exported frame independently and require exact lossless samples."""
    dimensions = json.loads((directory / "source.json").read_text(encoding="utf-8"))
    source = np.frombuffer((directory / "source.rgb").read_bytes(), dtype=np.uint8)
    source = source.reshape(dimensions["height"], dimensions["width"], 3)
    reports = []
    for name, suffix in ENCODINGS.items():
        dataset = pydicom.dcmread(directory / f"{name}.dcm")
        assert dataset.file_meta.TransferSyntaxUID == "1.2.840.10008.1.2" + suffix, name
        assert dataset.SOPClassUID == "1.2.840.10008.5.1.4.1.1.77.1.4", name
        assert dataset.SOPInstanceUID == dataset.file_meta.MediaStorageSOPInstanceUID, name
        assert dataset.SOPClassUID == dataset.file_meta.MediaStorageSOPClassUID, name
        assert dataset.StudyInstanceUID != dataset.SeriesInstanceUID, name
        assert len({dataset.StudyInstanceUID, dataset.SeriesInstanceUID, dataset.SOPInstanceUID}) == 3
        lossy = name.endswith("lossy") or name == "jpeg-baseline"
        assert dataset.LossyImageCompression == ("01" if lossy else "00"), name
        if lossy:
            assert float(dataset.LossyImageCompressionRatio) > 0, name
            assert dataset.LossyImageCompressionMethod, name
        if name.startswith("jpeg-xl"):
            with tempfile.TemporaryDirectory() as temporary:
                frame = Path(temporary) / "frame.jxl"
                decoded = Path(temporary) / "frame.png"
                frame.write_bytes(next(generate_frames(dataset.PixelData)))
                subprocess.run(["djxl", str(frame), str(decoded)], check=True, capture_output=True)
                pixels = np.asarray(Image.open(decoded))
        elif name == "jpeg-baseline":
            pixels = np.asarray(Image.open(BytesIO(next(generate_frames(dataset.PixelData)))).convert("RGB"))
        else:
            pixels = dataset.pixel_array
        assert pixels.shape == source.shape, name
        error = np.abs(pixels.astype(np.int32) - source)
        if not lossy:
            assert np.array_equal(pixels, source), f"{name}: lossless samples differ"
        reports.append({"encoding": name, "maximum_sample_error": int(error.max()),
                        "mean_absolute_sample_error": float(error.mean()), "lossless_exact": not lossy})
    return reports


def compare_python_views(directory: Path) -> None:
    """Check clinical mappings, with explicit reviewed declaration/orientation differences."""
    # Invoke with PYTHONPATH=python from the checkout. Runtime packages are not coupled.
    from dicom4ortho._generated_codes import IMAGE_TYPES, VIEWS  # pylint: disable=import-outside-toplevel
    from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph  # pylint: disable=import-outside-toplevel

    attributes = ["SeriesDescription", "PatientOrientation", "ImageLaterality", "DeviceSequence",
                  "AnatomicRegionSequence", "PrimaryAnatomicStructureSequence", "ViewCodeSequence",
                  "AcquisitionContextSequence", "RequestAttributesSequence"]
    for keyword in sorted(VIEWS):
        parameters = {"image_type": keyword}
        if keyword in ("IV28", "IV30", "EV40"):
            parameters["view_code_keyword"] = "projection_right"
        expected = OrthodonticPhotograph(**parameters).to_dataset()
        actual = pydicom.dcmread(directory / "views" / f"{keyword}.dcm")
        for attribute in attributes:
            if keyword in ("IV28", "IV30") and attribute == "PatientOrientation":
                # PS3.3 General Image Type 2C: emit empty, never invent orientation.
                assert attribute in actual and len(actual.PatientOrientation) == 0
                continue
            assert (attribute in expected) == (attribute in actual), (keyword, attribute)
            if attribute in expected:
                tag = expected.data_element(attribute).tag
                left = pydicom.Dataset()
                right = pydicom.Dataset()
                left.add(expected[tag])
                right.add(actual[tag])
                assert left.to_json_dict() == right.to_json_dict(), (keyword, attribute)
        view = IMAGE_TYPES[keyword]
        assert actual.ImageComments == f"{keyword}^{view.abbreviation}^{view.meaning}".replace("\xa0", " ")
        code = actual.RequestAttributesSequence[0].ScheduledProtocolCodeSequence[0]
        assert code.CodeValue == view.code.value
        assert code.CodingSchemeDesignator == view.code.scheme
        assert "ContextIdentifier" not in code  # No projection-CID extension on a protocol.
        assert len(actual.get("ViewCodeSequence", [])) <= 1


def validate_clinical_relationships(directory: Path) -> None:
    """Check independent serialized identity, progress, and worklist role evidence."""
    first = pydicom.dcmread(directory / "clinical-first.dcm")
    second = pydicom.dcmread(directory / "clinical-second.dcm")
    assert first.StudyInstanceUID == second.StudyInstanceUID
    assert first.SeriesInstanceUID == second.SeriesInstanceUID
    assert first.SOPInstanceUID != second.SOPInstanceUID
    assert first.AcquisitionDate == "20261021"
    assert first.AcquisitionContextSequence[-1].NumericValue == 0
    worklist = pydicom.dcmread(directory / "worklist.dcm")
    assert str(worklist.PhysiciansOfRecord) == "Provider^"
    assert str(worklist.OperatorsName) == "Operator^"
    assert str(worklist.ReferringPhysicianName) == "Referral^Doctor"
    assert worklist.RequestAttributesSequence[0].ScheduledProcedureStepID == "B"
    assert len(worklist.RequestAttributesSequence[0].ScheduledProtocolCodeSequence) == 2
    assert worklist.RequestAttributesSequence[0].RequestedProcedureID == "request-worklist"
    assert len(worklist.RequestAttributesSequence[0].RequestedProcedureCodeSequence) == 1
    series = pydicom.dcmread(directory / "series-requests.dcm")
    requests = series.RequestAttributesSequence
    assert [item.ScheduledProcedureStepID for item in requests] == ["A", "B"]
    assert requests[0].RequestedProcedureID == "request-A"
    assert [[code.CodeValue for code in item.ScheduledProtocolCodeSequence] for item in requests] == [
        ["EV01", "EV02", "EV01"], ["EV02"]]
    assert series.InstanceNumber == 999  # Not an inferred protocol index.
    assert "PerformedProtocolCodeSequence" not in series
    assert len(series.ViewCodeSequence) == 1


def main() -> None:
    """Report measured lossy errors without inventing clinical acceptance thresholds."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--compare-python", action="store_true")
    arguments = parser.parse_args()
    reports = validate(arguments.directory)
    validate_clinical_relationships(arguments.directory)
    if arguments.compare_python:
        compare_python_views(arguments.directory)
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
