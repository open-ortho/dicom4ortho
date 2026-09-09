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
    _SOC_SIZ_MARKER = b'\xff\x4f\xff\x51'   # Start of codestream, immediately followed by SIZ
    _COD_MARKER = 0x52                      # Coding style default
    _SOD_MARKER = 0x93                      # Start of data: pixel data begins, no more headers
    # Delimiting markers that carry no length field of their own.
    _MARKERS_WITHOUT_SEGMENT = frozenset({0x4F, 0xD9} | set(range(0xD0, 0xD9)))
    
    position = image_bytes.find(_SOC_SIZ_MARKER)
    if position < 0:
        raise ValueError("No JPEG 2000 codestream found: image does not contain SOC followed by SIZ.")

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
