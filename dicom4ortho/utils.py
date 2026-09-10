from typing import Optional
import uuid
from pydicom.dataset import Dataset
from dicom4ortho.config import DICOM4ORTHO_ROOT_UID

import logging
logger = logging.getLogger(__name__)


def generate_dicom_uid(root=None, hash=None):
    """
    A function to generate DICOM UIDs for new objects.

    If hash is not None, it will use that string to translate it to a DICOM UID. Useful if you want to produce the same UID for the same input file.

    hash has to be a 16 byte long bytes object.
    """
    new_uuid = hash or uuid.uuid4().bytes
    dicom_uid = root or DICOM4ORTHO_ROOT_UID or '2.25'
    for i in range(len(new_uuid)-len(dicom_uid.split('.'))):
        dicom_uid += '.' + str(new_uuid[i])

    logger.debug("Generated new Instance UID {}".format(dicom_uid))
    return dicom_uid


def jpeg2000_codestream(image_bytes: bytes) -> bytes:
    """
    Return the JPEG 2000 codestream in an image, unwrapping a JP2 container.

    DICOM's JPEG 2000 transfer syntaxes encapsulate the codestream in Pixel Data,
    never the surrounding JP2 container, so container input has to be unwrapped
    before it is stored. A file extension says nothing about which one it is: TOPS
    exports raw codestreams from files named ``.jp2``.

    Args:
        image_bytes: A raw JPEG 2000 codestream, or a JP2 container holding one.

    Returns:
        The codestream. The argument itself when it already is one, so a caller can
        pass anything JPEG 2000 without checking first.

    Raises:
        ValueError: If the image is neither a codestream nor a JP2 container, or if
            it is a container with no readable ``jp2c`` box.
    """
    # A raw codestream opens with the SOC marker, ISO/IEC 15444-1 Annex A.
    _SOC_MARKER = b'\xff\x4f'
    # A JP2 file opens with the signature box, ISO/IEC 15444-1 Annex I.5.1: a
    # length of 12, the type 'jP  ', then a fixed four-byte check value.
    _JP2_SIGNATURE = b'\x00\x00\x00\x0c\x6a\x50\x20\x20\x0d\x0a\x87\x0a'
    _JP2_CODESTREAM_BOX = b'jp2c'
    # Every box starts with a four-byte length and a four-byte type.
    _JP2_BOX_HEADER_LENGTH = 8

    if image_bytes.startswith(_SOC_MARKER):
        return image_bytes

    if not image_bytes.startswith(_JP2_SIGNATURE):
        raise ValueError(
            "Not JPEG 2000: the image starts with neither the SOC marker of a "
            "codestream nor the signature box of a JP2 container.")

    position = len(_JP2_SIGNATURE)
    while position + _JP2_BOX_HEADER_LENGTH <= len(image_bytes):
        length = int.from_bytes(image_bytes[position:position + 4], "big")
        box_type = image_bytes[position + 4:position + 8]
        content = position + _JP2_BOX_HEADER_LENGTH

        if length == 0:
            # ISO/IEC 15444-1 I.4: a length of zero means the box runs to the end
            # of the file, so there is nothing after it to skip to.
            end = len(image_bytes)
        elif length == 1:
            # A length of one means the real, 64-bit length follows the type.
            length = int.from_bytes(image_bytes[content:content + 8], "big")
            content += 8
            end = position + length
        else:
            end = position + length

        if box_type == _JP2_CODESTREAM_BOX:
            codestream = image_bytes[content:end]
            if not codestream.startswith(_SOC_MARKER):
                raise ValueError(
                    "Malformed JP2 container: the jp2c box does not hold a JPEG "
                    "2000 codestream.")
            return codestream

        if end <= position:
            raise ValueError(
                f"Malformed JP2 container: box at byte {position} declares a "
                f"length of {length}.")
        position = end

    raise ValueError("Malformed JP2 container: no jp2c box found.")


def jpeg2000_is_reversible(image_bytes: bytes) -> bool:
    """
    Return True when a JPEG 2000 codestream uses the reversible (lossless) wavelet
    by reading the header.

    The COD (Coding style Default) marker segment ends with the wavelet
    transformation field: 1 selects the 5/3 reversible transform (lossless), 0 the
    9/7 irreversible transform (lossy). See ISO/IEC 15444-1 Table A.17.

    Args:
        image_bytes: A raw JPEG 2000 codestream, or a JP2 container holding one.

    Returns:
        True if the codestream is losslessly compressed, False if it is lossy.

    Raises:
        ValueError: If no JPEG 2000 codestream with a readable COD marker is found.
    """
    # JPEG 2000 codestream markers, ISO/IEC 15444-1 Table A.2.
    _COD_MARKER = 0x52                      # Coding style default
    _SOD_MARKER = 0x93                      # Start of data: pixel data begins, no more headers
    # Delimiting markers that carry no length field of their own.
    _MARKERS_WITHOUT_SEGMENT = frozenset({0x4F, 0xD9} | set(range(0xD0, 0xD9)))

    # Unwrap first rather than searching for the SOC marker: in a container those
    # bytes can also occur inside a preceding metadata or thumbnail box, and
    # parsing from there would read something that is not the image.
    image_bytes = jpeg2000_codestream(image_bytes)
    position = 0

    while position < len(image_bytes) - 3:
        if image_bytes[position] != 0xFF:
            raise ValueError(f"Malformed JPEG 2000 codestream: expected a marker at byte {position}.")

        marker = image_bytes[position + 1]
        if marker == _COD_MARKER:
            segment_length = int.from_bytes(image_bytes[position + 2:position + 4], "big")
            segment = image_bytes[position + 4:position + 2 + segment_length]
            if not segment:
                raise ValueError("Malformed JPEG 2000 codestream: empty COD segment.")
            return segment[-1] == 1

        if marker in _MARKERS_WITHOUT_SEGMENT:
            position += 2
            continue

        if marker == _SOD_MARKER:
            raise ValueError("Malformed JPEG 2000 codestream: pixel data reached before any COD marker.")

        segment_length = int.from_bytes(image_bytes[position + 2:position + 4], "big")
        position += 2 + segment_length

    raise ValueError("Malformed JPEG 2000 codestream: no COD marker found.")


def get_scheduled_protocol_code(ds: Dataset) -> Optional[Dataset]:
    """
    Deprecated. Use get_image_type_code_dataset instead.
    """
    # Avoid circular import by importing here
    import warnings
    from dicom4ortho.m_orthodontic_photograph import OrthodonticPhotograph
    warnings.warn("get_scheduled_protocol_code is deprecated. Use get_image_type_code_dataset instead.",
                  DeprecationWarning, stacklevel=2)
    return OrthodonticPhotograph.get_image_type_code_dataset(ds)
