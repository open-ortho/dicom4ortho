""" A package to convert photographs stored in conventional formats (jpeg,
png, etc) into DICOM.

"""

import dicom4ortho.config
import logging
from dicom4ortho.assigning_authority import set_patient_id_assigning_authority
logger = logging.getLogger(__name__)

__version__ = dicom4ortho.config.VERSION
