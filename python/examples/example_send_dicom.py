# example_send_dicom.py

from dicom4ortho.controller import OrthodonticController

def main():
    # Initialize the controller
    controller = OrthodonticController()

    # Example DICOM files to send
    dicom_files = [
        'path/to/first.dicom',
        'path/to/second.dicom'
    ]

    # Example usage of sending DICOM files using DIMSE
    try:
        print("Sending DICOM files using DIMSE...")
        controller.send(
            dicom_files=dicom_files,
            send_method='dimse',
            pacs_dimse_hostname='192.168.0.1',
            pacs_dimse_port=104,
            pacs_dimse_aet='ORTHANC'
        )
        print("DICOM files have been sent via DIMSE.")
    except ValueError as e:
        print(f"An error occurred: {e}")

    # Example usage of sending DICOM files using WADO
    try:
        print("Sending DICOM files using WADO...")
        controller.send(
            dicom_files=dicom_files,
            send_method='wado',
            pacs_wado_url='http://dicomweb-server.com/dicomweb/studies',
            pacs_wado_username='user',
            pacs_wado_password='pass'
        )
        print("DICOM files have been sent via WADO.")
    except ValueError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
