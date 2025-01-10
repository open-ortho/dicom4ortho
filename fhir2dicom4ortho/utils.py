from PIL import Image
from io import BytesIO
import base64
from fhir.resources.binary import Binary
from pydicom import Dataset, dcmread

def convert_binary_to_image(binary: Binary) -> Image:
    # Decode the base64 data
    image_data = base64.b64decode(binary.data)

    # Create a BytesIO stream from the decoded data
    image_stream = BytesIO(image_data)

    # Open the image using PIL
    image = Image.open(image_stream)

    # If the content type is provided, use it to establish the kind of image
    if binary.contentType:
        image.format = binary.contentType.split('/')[-1].upper()

    return image

def convert_binary_to_dataset(binary: Binary) -> Dataset:
    # Decode the base64 data
    dicom_data = base64.b64decode(binary.data)

    # Create a BytesIO stream from the decoded data
    dicom_stream = BytesIO(dicom_data)

    # Read the DICOM dataset from the stream
    dataset = dcmread(dicom_stream)

    return dataset