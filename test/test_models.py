'''
Unit tests for model classes.

@author: Toni Magni
'''
from math import copysign
from unittest import TestCase
import logging
import datetime
from dicom4ortho.m_ada1107 import ADA1107
from dicom4ortho.model import DicomBase

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s', level=logging.INFO)


class Test(TestCase):

    def test_load_views(self):
        v = ADA1107()
        self.assertEquals(len(v.VIEWS), 74)
        self.assertGreater(len(v.VIEWS["VERSION"]), 0)
        self.assertGreater(len(v.CODES["VERSION"]), 0)
        logging.info(
            f'Views ver: [{v.VIEWS["VERSION"]}] Codes ver: [{v.CODES["VERSION"]}]')



class TestDicomBaseAcquisitionDateTimeSetter(TestCase):
    def setUp(self):
        # Assuming the class that contains the setter is named ImagingStudy
        self.dicombase = DicomBase()

    def test_with_timezone(self):
        # Test datetime with timezone
        dt_with_tz = datetime.datetime(2023, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
        self.dicombase.timezone = datetime.timezone(datetime.timedelta(hours=-5))  # New York Time
        self.dicombase.acquisition_datetime = dt_with_tz
        self.assertEqual(self.dicombase._ds.AcquisitionDateTime[-5:], '+0000')  # UTC timezone

    def test_without_timezone(self):
        # Test datetime without timezone, class timezone is set
        dt_without_tz = datetime.datetime(2023, 1, 1, 12, 0)
        self.dicombase.timezone = datetime.timezone(datetime.timedelta(hours=-5))  # New York Time
        self.dicombase.acquisition_datetime = dt_without_tz
        self.assertEqual(self.dicombase._ds.AcquisitionDateTime[-5:], '-0500')  # New York timezone

    def test_no_class_timezone(self):
        # Test datetime without timezone and no class timezone set
        dt_without_tz = datetime.datetime(2023, 1, 1, 12, 0)
        self.dicombase.timezone = None
        self.dicombase.acquisition_datetime = dt_without_tz
        # This checks if the timezone has been set to local timezone, may need to adjust based on local timezone
        # For example, if running in UTC environment, it should end with '+0000'
        expected_tz = datetime.datetime.now().astimezone().strftime('%z')
        self.assertEqual(self.dicombase._ds.AcquisitionDateTime[-5:], expected_tz)



class TestTimezoneSetterGetter(TestCase):

    def setUp(self):
        self.obj = DicomBase()  # Create an instance of your class

    def test_set_timezone_bruteforce(self):
        """ Tests for all possible timezones.
        """
        for hours in range(-12, 13):  # from -12 to +12 inclusive
            for minutes in [0, copysign(30,hours)]:  # checking on the hour and half-hour
                if abs(hours) == 12 and minutes != 0:
                    continue  # Skip the +12:30 and -12:30 cases

                logging.info(f"Testing {hours}:{minutes}")
                # Create timezone with current offset
                tz = datetime.timezone(datetime.timedelta(hours=hours, minutes=minutes))
                self.obj.timezone = tz

                # Expected format: +HHMM or -HHMM
                # Manual reconstruction is necessary to account for negative hours, and proper + sign addition.
                expected_sign = '+' if hours >= 0 else '-'
                expected_hours = abs(hours)
                expected_minutes = abs(int(minutes))
                expected_timezone = f"{expected_sign}{expected_hours:02d}{expected_minutes:02d}"

                # Check if TimezoneOffsetFromUTC is set correctly
                self.assertEqual(self.obj._ds.TimezoneOffsetFromUTC, expected_timezone)

    def test_set_timezone2(self):
        # Test setting a timezone
        tz = datetime.timezone(datetime.timedelta(hours=-5, minutes=-30))
        self.obj.timezone = tz

        # Check the set value directly
        set_tz = self.obj.timezone
        expected_tz = tz

        self.assertEqual(set_tz.utcoffset(None), expected_tz.utcoffset(None))

    def test_get_timezone(self):
        # Test getting a timezone
        self.obj._ds.TimezoneOffsetFromUTC = "-0700"

        tz = self.obj.timezone
        expected_tz = datetime.timezone(datetime.timedelta(hours=-7))

        # Check if the getter retrieves the correct timezone
        self.assertEqual(tz.utcoffset(None), expected_tz.utcoffset(None))

    def test_set_and_get_timezone(self):
        # Test setting and then getting a timezone
        tz = datetime.timezone(datetime.timedelta(hours=3, minutes=15))
        self.obj.timezone = tz

        retrieved_tz = self.obj.timezone

        # Check if the setter and getter are consistent
        self.assertEqual(retrieved_tz.utcoffset(None), tz.utcoffset(None))
