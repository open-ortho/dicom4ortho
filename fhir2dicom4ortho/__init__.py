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

args_cache = ArgsCache()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s')
logger = logging.getLogger(__name__)