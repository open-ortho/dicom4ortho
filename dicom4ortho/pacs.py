# dicom4ortho/pacs.py

import pydicom
from pynetdicom import AE, StoragePresentationContexts
import requests
from requests.auth import HTTPBasicAuth

def send_to_pacs_dimse(dicom_file_path, pacs_ip, pacs_port, pacs_aet):
    """Send DICOM file to PACS using DIMSE protocol."""
    dataset = pydicom.dcmread(dicom_file_path)

    ae = AE()
    ae.requested_contexts = StoragePresentationContexts

    assoc = ae.associate(pacs_ip, pacs_port, ae_title=pacs_aet)

    if assoc.is_established:
        status = assoc.send_c_store(dataset)
        if status:
            print('C-STORE request status: 0x{0:04x}'.format(status.Status))
        else:
            print('Connection timed out, was aborted, or received an invalid response')
        assoc.release()
    else:
        print('Failed to establish association')

    ae.shutdown()

def send_to_pacs_wado(dicom_file_path, dicomweb_url, username=None, password=None):
    """Send DICOM file to PACS using WADO/DICOMweb."""
    dataset = pydicom.dcmread(dicom_file_path)
    dicom_bytes = dataset.to_bytes()

    headers = {'Content-Type': 'application/dicom'}
    auth = HTTPBasicAuth(username, password) if username and password else None

    response = requests.post(dicomweb_url, headers=headers, data=dicom_bytes, auth=auth)

    if response.status_code in [200, 204]:
        print('DICOM instance successfully stored.')
    else:
        print(f'Failed to store DICOM instance. Status code: {response.status_code}')
        print('Response:', response.text)
