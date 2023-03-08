""" Codes and data defined from ADA-1107

Provides methods to download the data, and import it in Python objects.

"""

import urllib.request
import csv
from dicom4ortho.defaults import URL_ADA1107_CODES, URL_ADA1107_VIEWS

class ADA1107(object):
    CODES = {}
    VIEWS = {}
    def __init__(self) -> None:
        self._load_views()
        self._load_codes()

    def _load_views(self):
        # Override official location, if not yet published, for dev purposes
        URL_ADA1107_VIEWS = "file:///Users/afm/git/open-ortho/ada-1107/source/tables/views.csv"
        with urllib.request.urlopen(URL_ADA1107_VIEWS) as response:
            lines = [l.decode('utf-8').strip() for l in response.readlines()]
            reader = csv.DictReader(lines)
            for row in reader:
                key = row.pop('keyword')
                if key.startswith("VER:"):
                    self.VIEWS["VERSION"] = key.split(":")[1]
                else:
                    self.VIEWS[key] = row

    def _load_codes(self):
        # Override official location, if not yet published, for dev purposes
        URL_ADA1107_CODES = "file:///Users/afm/git/open-ortho/ada-1107/source/tables/codes.csv"
        with urllib.request.urlopen(URL_ADA1107_CODES) as response:
            lines = [l.decode('utf-8').strip() for l in response.readlines()]
            reader = csv.DictReader(lines)
            for row in reader:
                key = row.pop('keyword')
                if key == "__version__":
                    self.CODES["VERSION"] = row["code"]
                else:
                    self.CODES[key] = row
