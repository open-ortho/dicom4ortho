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

def get_scheduled_protocol_code(ds:Dataset) -> Dataset:
    """ Returns the code for the scheduled protocol pertaining to the passed Dataset.

    Was initially inside the OrthodonticPhotograph. However, better suited as a standalone function, since the OrthodonticPhotograph is not yet capable of being used to decode (kind of like loading an existing DICOM with a validate() method) and is not the only object that can have a ScheduledProtocolCode.

    Other modules can use it with more simplicity if it is here.
    """
    if 'RequestAttributesSequence' not in ds or ds.RequestAttributesSequence is None:
        logger.warning("Cannot identify this image: RequestAttributesSequence not present.")
        return None
    if 'ScheduledProtocolCodeSequence' not in ds.RequestAttributesSequence[0] or ds.RequestAttributesSequence[0].ScheduledProtocolCodeSequence is None:
        logger.warning("Cannot identify this image: ScheduledProtocolCodeSequence not present.")
        return None
    if 'InstanceNumber' not in ds or ds.InstanceNumber is None or ds.InstanceNumber == "":
        logger.warning("Cannot identify this image: InstanceNumber not present.")
        return None
    
    # As defined in DENT-OIP/ADA-1107, the IndexNumber of this image is also used to determine the ScheduledProtocolCode within its ScheduledProtocolCodeSequence.
    # There can be up to 100 instances of the same ScheduledProtocolCode, each with a different InstanceNumber. So all 100s are index 1, all 200s are index 2, etc.
    scheduled_protocol_index = int(ds.InstanceNumber) // 100
    try:
        return ds.RequestAttributesSequence[0].ScheduledProtocolCodeSequence[scheduled_protocol_index]
    except IndexError:
        logger.warning("Cannot identify this image: ScheduledProtocolCodeSequence does not have %s codes!", scheduled_protocol_index + 1)
        return None
    