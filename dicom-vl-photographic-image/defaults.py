import uuid

VERSION = '0.0.1'
date_format = '%Y%m%d'
time_format = '%H%M%S.%f'

# This is a unique ID generated for this specific software only.
#  * Random generation using generate_dicom_uid() below
#  * Append Version of software to distinguish between different releases
#  * Should always be constant, just change with version numbers
ImplementationClassUID = '2.25.34.34.153.156.139.154.17.234.176.144.0.5.27.208.218.88.' + VERSION

def generate_dicom_uid():
    print("Generating new Instance UID...")
    uuid = uuid.uuid4().bytes
    dicom_uid = '2.25'
    for i in range(len(uuid)):
        dicom_uid += '.' + str(uuid[i])

    return dicom_uid

