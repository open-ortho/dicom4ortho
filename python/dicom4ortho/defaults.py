""" Deprecated module. Use utils and config.
"""

import logging
logger = logging.getLogger(__name__)
logger.warning("DEPRECATION WARNING: dicom4ortho.defaults is deprecated. Make use of dicom4orto.config and dicom4ortho.utils instead.")

from dicom4ortho.utils import generate_dicom_uid
from dicom4ortho.config import *