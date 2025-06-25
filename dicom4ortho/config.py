"""
Configurations, defaults and constants
"""

import re
from pathlib import Path
import importlib.resources as importlib_resources

VERSION = '0.5.1'
PROJECT_NAME = 'dicom4ortho'
__url__ = 'https://github.com/open-ortho/dicom4ortho'
__author__ = 'Toni Magni'
__email__ = 'open-ortho@panio.info'
__updated__ = ''
__short_description__ = 'A package to convert photographs stored in conventional formats (jpeg, png, etc) into DICOM.'
__creation_date__ = '2020-05-01'


DICOM3TOOLS_PATH = Path('modules','dicom3tools')

# Date format used when importing date from CSV file.
# The date in the CSV file should be in this format.
IMPORT_DATE_FORMAT = '%Y-%m-%d'
IMPORT_TIME_FORMAT = '%H%M%S.%f'

# Date format in DICOM file
DATE_FORMAT = '%Y%m%d'
TIME_FORMAT = '%H%M%S.%f'
DICOM_PREAMBLE = b'\0' * 128

URL_DENT_OIP_VIEWS = importlib_resources.files('dicom4ortho.resources') /'views.csv'
URL_DENT_OIP_VIEWS = URL_DENT_OIP_VIEWS.as_uri()
URL_DENT_OIP_CODES = importlib_resources.files('dicom4ortho.resources') /'codes.csv'
URL_DENT_OIP_CODES = URL_DENT_OIP_CODES.as_uri()

# This is a unique ID generated for this specific software only.
#  * Random generation using generate_dicom_uid() below
#  * Append Version of software to distinguish between different releases
#  * Should always be constant, just change with version numbers. splitting out -dev or other version postfix
#  * Max length 64. Cannot contain characters.
DICOM4ORTHO_ROOT_UID = '1.3.6.1.4.1.61741.11.2'

# VL Dental View CID we need to extend to include private codes.
VL_DENTAL_VIEW_CID = '4063'

# Schema Copied from DCMTK assignment
stripped_version = re.sub(r'[^0-9]', '', VERSION)
version_2 = re.sub(r'[^0-9\.]', '', VERSION)
ImplementationVersionName = f"{PROJECT_NAME.upper()}_{stripped_version}"[0:15] # Truncate to 16 characters allowed.
ImplementationClassUID = f"{DICOM4ORTHO_ROOT_UID}.0.{version_2}"
MediaStorageSOPInstanceUID_ROOT = f"{DICOM4ORTHO_ROOT_UID}.1"
StudyInstanceUID_ROOT = f"{DICOM4ORTHO_ROOT_UID}.2"
SeriesInstanceUID_ROOT = f"{DICOM4ORTHO_ROOT_UID}.3"
SOPInstanceUID_ROOT = f"{DICOM4ORTHO_ROOT_UID}.4"
 

# The default IDs used for SeriesNumber StudyID and InstanceNumber
IDS_NUMBERS = '000'

# This is populated by controller.OrthodonticController._load_image_types()
image_types = {}

