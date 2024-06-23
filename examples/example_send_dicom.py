# example_send_dicom.py

from dicom4ortho.controller import SimpleController

def main():
    # Initialize the controller
    controller = SimpleController()

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
            pacs_ip='192.168.0.1',
            pacs_port=104,
            pacs_aet='ORTHANC'
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
            dicomweb_url='http://dicomweb-server.com/dicomweb/studies',
            username='user',
            password='pass'
        )
        print("DICOM files have been sent via WADO.")
    except ValueError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
