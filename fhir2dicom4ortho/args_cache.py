""" Configuration and variables.

Class to get options from env variables.

Argparse support was purposely removed, because it was creating too much trouble with unittests, and too much overhead. Arguments can be just as easily passed as env vars, and since this is a server, not a tool to be used every day, arguments should not be necessary anyways.

"""
import os
from distutils.util import strtobool


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ArgsCache:
    _args = None

    @staticmethod
    def get_arguments(test_args=None):
        if test_args is not None:
            return Namespace(**test_args)
        if ArgsCache._args is None:
            ArgsCache._args = ArgsCache.load_arguments()
        return ArgsCache._args

    @staticmethod
    def load_arguments():
        # Create an object similar to argparse.Namespace
        return Namespace(
            # The path of the SQLite DB file for the local mapping.
            verbosity=os.getenv('F2D4O_VERBOSITY', 0),

            # FHIR API server IP and port.
            fhir_api=bool(strtobool(os.getenv('F2D4O_FHIR_API', 'True'))),
            fhir_listen=os.getenv('F2D4O_FHIR_LISTEN', '*'),
            fhir_port=int(os.getenv('F2D4O_FHIR_PORT','8000')),

            pacs_send_method=os.getenv('F2D4O_PACS_SEND_METHOD', 'dimse'),

            # DICOM PACS destination WADO coordinates.
            pacs_wado_url=os.getenv('F2D4O_PACS_WADO_URL', ''),
            pacs_wado_username=os.getenv('F2D4O_PACS_WADO_USERNAME', ''),
            pacs_wado_password=os.getenv('F2D4O_PACS_WADO_PASSWORD', ''),

            # DICOM PACS destination DIMSE coordinates.
            pacs_dimse_aet=os.getenv('F2D4O_PACS_DIMSE_AET', ''),
            pacs_dimse_hostname=os.getenv('F2D4O_PACS_DIMSE_IP', ''),
            pacs_dimse_port=int(os.getenv('F2D4O_PACS_DIMSE_PORT', '104')),

        )
