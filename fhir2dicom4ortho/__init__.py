"""
fhir2dicom4ortho package

This package provides a web service that accepts images and metadata using the FHIR API. 
It utilizes the dicom4ortho package to convert the received images into DICOM format 
and uploads them to a PACS (Picture Archiving and Communication System).

Features:
- Accepts images and metadata via FHIR API
- Converts images to DICOM format
- Uploads DICOM images to PACS

Dependencies:
- dicom4ortho
- fhir.resources
- httpx
- fastapi
"""
import logging
from fhir2dicom4ortho.args_cache import ArgsCache

verbosity_mapping = {
    0: logging.WARNING,  # Default to WARNING if -v is not provided
    1: logging.INFO,
    2: logging.DEBUG
}
args_cache = ArgsCache().load_arguments()

level = verbosity_mapping.get(args_cache.verbosity, logging.DEBUG)
logging.basicConfig(level=level)
root_logger = logging.getLogger()
root_logger.setLevel(level)

# Set the format for all handlers of the root logger
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
for handler in root_logger.handlers:
    handler.setFormatter(formatter)

root_logger.propagate = True
logger = logging.getLogger(__name__)