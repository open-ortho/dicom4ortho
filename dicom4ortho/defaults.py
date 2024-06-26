"""
Defaults and Constants.
"""

import re
import uuid
import logging
from pathlib import Path
import importlib.resources as importlib_resources

VERSION = '0.3.8'
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

URL_ADA1107_VIEWS = importlib_resources.files('dicom4ortho.resources') /'views.csv'
URL_ADA1107_VIEWS = URL_ADA1107_VIEWS.as_uri()
URL_ADA1107_CODES = importlib_resources.files('dicom4ortho.resources') /'codes.csv'
URL_ADA1107_CODES = URL_ADA1107_CODES.as_uri()

# This is a unique ID generated for this specific software only.
#  * Random generation using generate_dicom_uid() below
#  * Append Version of software to distinguish between different releases
#  * Should always be constant, just change with version numbers. splitting out -dev or other version postfix
#  * Max length 64. Cannot contain characters.
DICOM4ORTHO_ROOT_UID = '1.3.6.1.4.1.61741.11.2'

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

ADD_MAX_ALLOWED_TEETH = 'ALL'

# This is populated by controller.SimpleController._load_image_types()
image_types = {}

def generate_dicom_uid(root=None, hash=None):
    """
    A function to generate DICOM UIDs for new objects.

    If hash is not None, it will use that string to translate it to a DICOM UID. Useful if you want to produce the same UID for the same input file.

    hash has to be a 16 byte long bytes object.
    """
    new_uuid = hash or uuid.uuid4().bytes
    dicom_uid = root or '2.25'
    for i in range(len(new_uuid)-len(dicom_uid.split('.'))):
        dicom_uid += '.' + str(new_uuid[i])

    logging.debug("Generated new Instance UID {}".format(dicom_uid))
    return dicom_uid
