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
        self.assertEqual(len(v.VIEWS), 74)
        self.assertGreater(len(v.VIEWS["VERSION"]), 0)
        self.assertGreater(len(v.CODES["VERSION"]), 0)
        logging.info(
            f'Views ver: [{v.VIEWS["VERSION"]}] Codes ver: [{v.CODES["VERSION"]}]')



class TestDicomBaseAcquisitionDateTimeSetter(TestCase):
    """ Test AcquisitionDateTime in various circumstances.

    - What if the acquisitionDateTime comes in with a timezone which is different from TimezoneOffsetFromUTC? No problem, they are just both TZ aware.
    - 
    """
    def setUp(self):
        # Assuming the class that contains the setter is named ImagingStudy
        self.dicombase = DicomBase()

    def test_with_timezone(self):
        """ Scenario where both AcquisitionDate and TZOffset are both present.

        AcquisitionDateTime should always have priority.
        """
        # Test datetime with timezone
        dt_with_tz = datetime.datetime(2023, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
        self.dicombase.timezone = datetime.timezone(datetime.timedelta(hours=-5))  # New York Time
        self.dicombase.acquisition_datetime = dt_with_tz
        self.assertEqual(self.dicombase._ds.AcquisitionDateTime[-5:], '+0000')  # UTC timezone

    def test_without_timezone(self):
        """ Scenario where AcquisitionDate is w/o TZ, and TZOffset is present.

        AcquisitionDateTime should use TZ from TZOffset.
        """
        # Test datetime without timezone, class timezone is set
        dt_without_tz = datetime.datetime(2023, 1, 1, 12, 0)
        self.dicombase.timezone = datetime.timezone(datetime.timedelta(hours=-5))  # New York Time
        self.dicombase.acquisition_datetime = dt_without_tz
        self.assertEqual(self.dicombase._ds.AcquisitionDateTime[-5:], '-0500')  # New York timezone

    def test_no_class_timezone(self):
        """ Scenario where AcquisitionDateTime is without timezone and TZOffset also doesn't exist.

        Should return a time with the TZ of the running server, which is ourselves.
        """
        # Test datetime without timezone and no class timezone set
        dt_without_tz = datetime.datetime(2023, 1, 1, 12, 0)
        self.dicombase.timezone = None
        self.dicombase.acquisition_datetime = dt_without_tz

        # This check verifies if the timezone has been set to the local timezone.
        # Adjustments might be necessary based on the local environment's timezone settings.
        # For instance, in a UTC environment, the expected result should be '+0000'.
        # Using astimezone() considers daylight saving time based on the provided date,
        # hence it's inappropriate to rely on datetime.datetime.now() solely for timezone testing.
        expected_tz = dt_without_tz.astimezone().strftime('%z')
        self.assertEqual(self.dicombase._ds.AcquisitionDateTime[-5:], expected_tz)



class TestTimezoneSetterGetter(TestCase):

    def setUp(self):
        self.obj = DicomBase()  # Create an instance of your class

    def test_set_TimezoneOffsetFromUTC(self):
        """ Test if the DICOM TimezoneOffsetFromUTC is set properly.

        Tests for all possible timezones.
        """
        for hours in range(-12, 13):  # from -12 to +12 inclusive
            for minutes in [0, int(copysign(30,hours))]:  # checking on the hour and half-hour
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

    def test_set_and_get_timezone(self):
        """ Test if the timezone attribute properly returns the set timezone.

        There is a different logic between the internal timezone setting and the DICOM TimezoneOffsetFromUTC.
        """
        for hours in range(-12, 13):  # from -12 to +12 inclusive
            for minutes in [0, int(copysign(30,hours))]:  # checking on the hour and half-hour
                if abs(hours) == 12 and minutes != 0:
                    continue  # Skip the +12:30 and -12:30 cases

                logging.info(f"Testing {hours}:{minutes}")
                # Test setting a timezone
                tz = datetime.timezone(datetime.timedelta(hours=hours, minutes=minutes))
                self.obj.timezone = tz

                # Check the set value directly
                set_tz = self.obj.timezone
                expected_tz = tz

                self.assertEqual(set_tz.utcoffset(None), expected_tz.utcoffset(None),msg=f"Error while testing {hours}h {minutes}m")
