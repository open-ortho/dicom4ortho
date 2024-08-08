""" Codes and data defined from DENT-OIP

Provides methods to download the DENT-OIP specifications in CSV and import it in a Python dictionary.

"""

import urllib.request
import csv
from dicom4ortho.config import URL_DENT_OIP_CODES, URL_DENT_OIP_VIEWS
import logging
logger = logging.getLogger(__name__)

class DENT_OIP(object):
    CODES = {}
    VIEWS = {}

    def __init__(self,url_codes=None, url_views=None) -> None:
        if not url_codes:
            url_codes = URL_DENT_OIP_CODES
        if not url_views:
            url_views = URL_DENT_OIP_VIEWS

        self._load_views(url=url_views)
        self._load_codes(url=url_codes)

    def _load_views(self, url) -> None:
        # Override official location, if not yet published, for dev purposes
        with urllib.request.urlopen(url) as response:
            lines = [l.decode('utf-8').strip() for l in response.readlines()]
            reader = csv.DictReader(lines)
            for row in reader:
                key = row.pop('keyword')
                if key.startswith("VER:"):
                    self.VIEWS["VERSION"] = key.split(":")[1]
                else:
                    self.VIEWS[key] = row

    def _load_codes(self, url) -> None:
        # Override official location, if not yet published, for dev purposes
        with urllib.request.urlopen(url) as response:
            lines = [l.decode('utf-8').strip() for l in response.readlines()]
            reader = csv.DictReader(lines)
            for row in reader:
                key = row.pop('keyword')
                if key == "__version__":
                    self.CODES["VERSION"] = row["code"]
                else:
                    self.CODES[key] = row
