from typing import Optional
import uuid
from pydicom.dataset import Dataset
from dicom4ortho.config import DICOM4ORTHO_ROOT_UID, VL_DENTAL_VIEW_CID

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
