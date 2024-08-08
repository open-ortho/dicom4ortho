""" Deprecated module. Use utils and config.
"""

import logging
logger = logging.getLogger(__name__)
logger.warning("DEPRECATION WARNING: dicom4ortho.defaults is deprecated. Make use of dicom4orto.config and dicom4ortho.utils instead.")

from dicom4ortho.utils import generate_dicom_uid
from dicom4ortho.config import *
from dicom4ortho.config import __author__, __creation_date__, __email__, __short_description__, __updated__, __url__
