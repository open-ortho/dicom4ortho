from typing import Optional
import uuid
from pydicom.dataset import Dataset
from dicom4ortho.config import DICOM4ORTHO_ROOT_UID, DICOM4ORTHO_VIEW_CID

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


def get_image_type_code_sequence(ds: Dataset) -> Optional[Dataset]:
    """
    Returns the first code item from ViewCodeSequence with the proprietary Context Identifier (CID).
    Only returns items where the item's ContextIdentifier matches DICOM4ORTHO_VIEW_CID.
    """
    view_seq = getattr(ds, 'ViewCodeSequence', None)
    if not view_seq:
        logger.warning("Cannot identify this image: ViewCodeSequence not present.")
        return None
    for item in view_seq:
        cid = getattr(item, 'ContextIdentifier', None)
        if cid == DICOM4ORTHO_VIEW_CID:
            return item
    logger.warning("No ViewCodeSequence item with proprietary ContextIdentifier found.")
    return None


def get_scheduled_protocol_code(ds: Dataset) -> Optional[Dataset]:
    """
    Deprecated. Use get_image_type_code_sequence instead.
    """
    import warnings
    warnings.warn("get_scheduled_protocol_code is deprecated. Use get_image_type_code_sequence instead.",
                  DeprecationWarning, stacklevel=2)
    return get_image_type_code_sequence(ds)
