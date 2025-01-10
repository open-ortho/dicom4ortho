from fhir2dicom4ortho import logger
from fhir2dicom4ortho.args_cache import ArgsCache
from logging import WARNING, INFO, DEBUG

verbosity_mapping = {
    0: WARNING,  # Default to WARNING if -v is not provided
    1: INFO,
    2: DEBUG
}

def fhir_api():
    args = ArgsCache.get_arguments()
    level = verbosity_mapping.get(args.verbosity, DEBUG)
    logger.setLevel(level)
    logger.propagate = True

    logger.debug(("Logging Level is {}".format(
        logger.getEffectiveLevel())))

    import uvicorn
    logger.info(f"Lighting a FHIR API on {args.fhir_listen}:{args.fhir_port}")
    uvicorn.run("fhir2dicom4ortho.fhir_api:fhir_api_app", host=args.fhir_listen, port=args.fhir_port)