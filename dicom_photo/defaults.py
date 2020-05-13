"""
Defaults and Constants.
"""

import uuid

VERSION = '0.1.0'
__url__ = 'https://github.com/orgs/open-ortho'
__author__ = 'Toni Magni'
__email__ = 'open-ortho@panio.info'
__updated__ = ''
__short_description__ = 'A package to convert photographs stored in conventional formats (jpeg, png, etc) into DICOM.'
__creation_date__ = '2020-05-01'


DICOM3TOOLS_PATH = '/Users/cdstaff/dev/open-ortho/dicom-photography/resources/dicom3tools_macexe_1.00.snapshot.20191225051647'

DATE_FORMAT = '%Y%m%d'
TIME_FORMAT = '%H%M%S.%f'
DICOM_PREAMBLE = b'\0' * 128

# This is a unique ID generated for this specific software only.
#  * Random generation using generate_dicom_uid() below
#  * Append Version of software to distinguish between different releases
#  * Should always be constant, just change with version numbers
IMPLEMENTATION_CLASS_UID = '2.25.34.34.153.156.139.154.17.234.176.144.0.5.27.208.218.88.' + VERSION

def generate_dicom_uid():
    """
    A function to generate DICOM UIDs for new objects.
    """
    print("Generating new Instance UID...")
    new_uuid = uuid.uuid4().bytes
    dicom_uid = '2.25'
    for i in range(len(uuid)):
        dicom_uid += '.' + str(new_uuid[i])

    return dicom_uid
