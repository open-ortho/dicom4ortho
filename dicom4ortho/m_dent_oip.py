""" Codes and data defined from DENT-OIP

Provides typed data classes for DICOM codes and orthodontic views, plus legacy
CSV loading used during the transition to generated code.

"""

from __future__ import annotations

import urllib.request
import csv
from dataclasses import dataclass, field
from typing import Optional

from pydicom.dataset import Dataset
from pydicom.sequence import Sequence

from dicom4ortho.config import URL_DENT_OIP_CODES, URL_DENT_OIP_VIEWS
import logging
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Typed data layer
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DicomCode:
    """A single DICOM coded entry (code value, scheme designator, code meaning)."""

    value: str
    scheme: str
    meaning: str

    def to_dataset(self) -> Dataset:
        """Return a pydicom Dataset representing this code."""
        ds = Dataset()
        ds.CodeValue = self.value
        ds.CodingSchemeDesignator = self.scheme
        ds.CodeMeaning = self.meaning[:64]  # LO max 64 chars
        return ds

    def to_sequence(self) -> Sequence:
        """Return a single-item pydicom Sequence wrapping this code."""
        return Sequence([self.to_dataset()])


@dataclass(frozen=True)
class OrthoView:
    """A fully-typed representation of one row in views.csv.

    Field names follow CP-1570 / TID 3465 terminology.

    TID 3465 AcquisitionContextSequence rows:
      Row 1 – CN: OrthognathicFunctionalCondition (130325, DCM), BCID 4066
      Row 2 – CN: FindingByInspection (118243007, SCT), BCID 4067
      Row 3 – CN: ObservableEntity (363787002, SCT), BCID 4068
      Row 4 – CN: DentalOcclusion (25272006, SCT), BCID 4069
      Rows 5-6 – LongitudinalTemporalEventType + Offset are per-session,
                 set by the library user at runtime via OrthodonticPhotograph.
    """

    keyword: str

    # PatientOrientation (0020,0020) — None when orientation cannot be
    # determined for the view (e.g. IV28, IV30 "Can Vary").
    patient_orientation: Optional[tuple[str, str]]

    # ImageLaterality (0020,0062) — raw CS value e.g. "U", "L", "R", "B"
    image_laterality: str

    # AnatomicRegionSequence (0008,2218)
    anatomic_region: DicomCode

    # AnatomicRegionModifierSequence (0008,2220) — nested inside anatomic_region
    anatomic_region_modifier: Optional[DicomCode]

    # PrimaryAnatomicStructureSequence (0008,2228)
    primary_anatomic_structure: Optional[DicomCode]

    # PrimaryAnatomicStructureModifierSequence (0008,2230)
    primary_anatomic_structure_modifier: Optional[DicomCode]

    # DeviceSequence (0050,0010)
    devices: tuple[DicomCode, ...]

    # ViewCodeSequence (0054,0220)
    view_code: Optional[DicomCode]

    # ViewModifierCodeSequence (0054,0222) — nested inside view_code
    view_modifiers: tuple[DicomCode, ...]

    # AcquisitionContextSequence — TID 3465 rows 1-4
    orthognathic_functional_conditions: tuple[DicomCode, ...]
    findings_by_inspection: tuple[DicomCode, ...]
    observable_entities: tuple[DicomCode, ...]
    dental_occlusion: Optional[DicomCode]

    # Human-readable labels
    description: str        # → ImageComments
    series_description: str  # → SeriesDescription


# ---------------------------------------------------------------------------
# Legacy CSV loader (kept for transition; removed in Step 4 refactor)
# ---------------------------------------------------------------------------

class DENT_OIP(object):
    CODES = {}
    VIEWS = {}

    def __init__(self, url_codes=None, url_views=None) -> None:
        if not url_codes:
            url_codes = URL_DENT_OIP_CODES
        if not url_views:
            url_views = URL_DENT_OIP_VIEWS

        self._load_views(url=url_views)
        self._load_codes(url=url_codes)

    def _load_views(self, url) -> None:
        # Override official location, if not yet published, for dev purposes
        with urllib.request.urlopen(url) as response:
            lines = [l.decode('utf-8').strip() for l in response.readlines()]
            reader = csv.DictReader(lines)
            for row in reader:
                key = row.pop('keyword')
                if key.startswith("VER:"):
                    self.VIEWS["VERSION"] = key.split(":")[1]
                else:
                    self.VIEWS[key] = row

    def _load_codes(self, url) -> None:
        # Override official location, if not yet published, for dev purposes
        with urllib.request.urlopen(url) as response:
            lines = [l.decode('utf-8').strip() for l in response.readlines()]
            reader = csv.DictReader(lines)
            for row in reader:
                key = row.pop('keyword')
                if key == "__version__":
                    self.CODES["VERSION"] = row["code"]
                else:
                    self.CODES[key] = row
