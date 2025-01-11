from PIL import Image
from io import BytesIO
from fhir.resources.binary import Binary
from pydicom import Dataset, dcmread
from fhir2dicom4ortho import logger

def convert_binary_to_image(binary: Binary) -> Image:
    image_data = binary.data

    logger.debug(f"Decoded image data length: {len(image_data)}")
    logger.debug(f"Content type: {binary.contentType}")
    logger.debug(f"First 20 bytes of image data: {image_data[:20]}")

    # Create a BytesIO stream from the decoded data
    image_stream = BytesIO(image_data)

    # Open the image using PIL
    image = Image.open(image_stream)
    logger.debug(f"Image format: {image.format}")
    # If the content type is provided, use it to establish the kind of image
    if binary.contentType:
        image_format = binary.contentType.split('/')[-1].upper()
        logger.debug(f"Image format: {image_format}")
        image.format = image_format

    return image

def convert_binary_to_dataset(binary: Binary) -> Dataset:
    # Decode the base64 data
    dicom_data = binary.data

    # Create a BytesIO stream from the decoded data
    dicom_stream = BytesIO(dicom_data)

    # Read the DICOM dataset from the stream
    dataset = dcmread(dicom_stream)

    return dataset