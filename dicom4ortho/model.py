"""
The model.
"""
import datetime
import logging
import io
from math import copysign

from pydicom.sequence import Sequence
from pydicom.dataset import FileDataset, DataElement, FileMetaDataset
from pydicom.datadict import tag_for_keyword
from pydicom.encaps import encapsulate
from pydicom.uid import JPEGBaseline8Bit, JPEGExtended12Bit, ImplicitVRLittleEndian, ExplicitVRBigEndian, ExplicitVRLittleEndian, JPEGLosslessSV1, RLELossless, JPEGLosslessP14, JPEG2000
from pydicom import dcmread as pydicom_dcmread
import numpy

# pylint: disable=no-name-in-module
from pynetdicom.sop_class import VLPhotographicImageStorage
from PIL import Image

import dicom4ortho.defaults as defaults


class DicomBase(object):
    """ Functions and fields common to most DICOM images.
    """

    def __init__(self, **kwargs):
        self.sop_instance_uid = kwargs.get(
            "sop_instance_uid") or defaults.generate_dicom_uid()
        self.time_string = datetime.datetime.now().strftime(defaults.TIME_FORMAT)
        self.date_string = datetime.datetime.now().strftime(defaults.DATE_FORMAT)
        self.input_image_filename = kwargs.get('input_image_filename')
        self.output_image_filename = kwargs.get('output_image_filename')
        self.file_meta = FileMetaDataset()
        self._ds = None
        self._set_dataset()
        self._set_general_series()
        self._set_general_study()
        self._set_general_image()
        self._set_acquisition_context()
        self._set_sop_common()

    def set_file_meta(self):
        self.file_meta.MediaStorageSOPInstanceUID = self.sop_instance_uid
        self.file_meta.ImplementationClassUID = defaults.IMPLEMENTATION_CLASS_UID

    def _set_dataset(self):
        self._ds = FileDataset(
            self.output_image_filename,
            {},
            file_meta=self.file_meta,
            preamble=defaults.DICOM_PREAMBLE)

        self._ds.PatientName = "^"

    def _set_general_study(self):
        self._ds.AccessionNumber = ''
        self._ds.StudyInstanceUID = defaults.generate_dicom_uid()
        self._ds.StudyID = defaults.IDS_NUMBERS
        self._ds.StudyDate = self.date_string
        self._ds.StudyTime = self.time_string

    def _set_general_series(self):
        self._ds.SeriesInstanceUID = defaults.generate_dicom_uid()
        self._ds.SeriesNumber = defaults.IDS_NUMBERS

    def _set_general_image(self):
        self._ds.InstanceNumber = defaults.IDS_NUMBERS
        self._ds_PatientOrientation = ''

    def _set_acquisition_context(self):
        self._ds.AcquisitionContextSequence = Sequence([])

    def _set_sop_common(self):
        self._ds.SpecificCharacterSet = "ISO_IR 192" # UTF-8
        self._ds.SOPInstanceUID = self.sop_instance_uid
        self._ds.TimezoneOffsetFromUTC = datetime.datetime.now().astimezone().strftime("%z")

    def _set_name(self, tagname, name, position):
        """ Helper function for setting firstname of PN Datatype

        :param position: set to 1 for firstname, 0 for lastname.
        """
        if tagname not in self._ds:
            self._ds[tagname] = DataElement(
                tag_for_keyword(tagname), 'PN', "^")

        newpart = name
        oldpart = str(self._ds[tagname].value).split('^')[position]
        if position == 0:
            firstname = newpart
            lastname = oldpart
        elif position == 1:
            firstname = oldpart
            lastname = newpart

        value = f"{lastname}^{firstname}"

        self._ds[tagname] = DataElement(
            tag_for_keyword(tagname), 'PN', value)

    @ property
    def series_datetime(self):
        return datetime.datetime.strptime(
            f"{self._ds.SeriesDate}{self._ds.SeriesTime}",
            f"{defaults.DATE_FORMAT}{defaults.TIME_FORMAT}"
        )

    @ series_datetime.setter
    def series_datetime(self, _seriesdatetime):
        self._ds.SeriesTime = _seriesdatetime.strftime(defaults.TIME_FORMAT)
        self._ds.SeriesDate = _seriesdatetime.strftime(defaults.DATE_FORMAT)

    @ property
    def study_datetime(self):
        return datetime.datetime.strptime(
            f"{self._ds.StudyDate}{self._ds.StudyTime}",
            f"{defaults.DATE_FORMAT}{defaults.TIME_FORMAT}"
        )

    @ study_datetime.setter
    def study_datetime(self, _studydatetime):
        self._ds.StudyTime = _studydatetime.strftime(defaults.TIME_FORMAT)
        self._ds.StudyDate = _studydatetime.strftime(defaults.DATE_FORMAT)

    @ property
    def study_instance_uid(self):
        return self._ds.StudyInstanceUID

    @ study_instance_uid.setter
    def study_instance_uid(self, uuid):
        self._ds.StudyInstanceUID = uuid

    @ property
    def series_instance_uid(self):
        return self._ds.SeriesInstanceUID

    @ series_instance_uid.setter
    def series_instance_uid(self, uuid):
        self._ds.SeriesInstanceUID = uuid

    @ property
    def operator_firstname(self):
        return str(self._ds.OperatorsName).split('^')[1]

    @ operator_firstname.setter
    def operator_firstname(self, firstname):
        self._set_name("OperatorsName", firstname, 0)

    @ property
    def operator_lastname(self):
        return str(self._ds.OperatorsName).split('^')[0]

    @ operator_lastname.setter
    def operator_lastname(self, lastname):
        self._set_name("OperatorsName", lastname, 1)

    @ property
    def institution_address(self):
        return self._ds.InstitutionAddress

    @ institution_address.setter
    def institution_address(self, address):
        self._ds.InstitutionAddress = address

    @ property
    def institution_name(self):
        return self._ds.InstitutionName

    @ institution_name.setter
    def institution_name(self, name):
        self._ds.InstitutionName = name

    @ property
    def study_description(self):
        return self._ds.StudyDescription

    @ study_description.setter
    def study_description(self, description):
        self._ds.StudyDescription = description

    @ property
    def series_description(self):
        return self._ds.SeriesDescription

    @ series_description.setter
    def series_description(self, description):
        self._ds.SeriesDescription = description

    @ property
    def patient_firstname(self):
        return str(self._ds.PatientName).split('^')[1]

    @ patient_firstname.setter
    def patient_firstname(self, firstname):
        self._set_name("PatientName", firstname, 0)

    @ property
    def patient_lastname(self):
        return str(self._ds.PatientName).split('^')[0]

    @ patient_lastname.setter
    def patient_lastname(self, lastname):
        self._set_name("PatientName", lastname, 1)

    @ property
    def patient_id(self):
        return self._ds.PatientID

    @ patient_id.setter
    def patient_id(self, patient_id):
        # Patient ID in DICOM must be a String.
        self._ds.PatientID = str(patient_id)

    @ property
    def reason_for_visit(self):
        return self._ds.ReasonForVisit

    @ reason_for_visit.setter
    def reason_for_visit(self, reason):
        self._ds.ReasonForVisit = reason

    @ property
    def patient_sex(self):
        return self._ds.PatientSex

    @ patient_sex.setter
    def patient_sex(self, patient_sex):
        self._ds.PatientSex = patient_sex

    @ property
    def patient_birthdate(self):
        return datetime.datetime.strptime(self._ds.PatientBirthDate, defaults.DATE_FORMAT).date()

    @ patient_birthdate.setter
    def patient_birthdate(self, patient_birthdate):
        self._ds.PatientBirthDate = patient_birthdate.strftime(
            defaults.DATE_FORMAT)

    @ property
    def performing_physician_firstname(self):
        return str(self._ds.PerformingPhysicianName).split('^')[1]

    @ performing_physician_firstname.setter
    def performing_physician_firstname(self, firstname):
        self._set_name("PerformingPhysicianName", firstname, 0)

    @ property
    def performing_physician_lastname(self):
        return str(self._ds.PerformingPhysicianName).split('^')[0]

    @ performing_physician_lastname.setter
    def performing_physician_lastname(self, lastname):
        self._set_name("PerformingPhysicianName", lastname, 1)

    @ property
    def dental_provider_firstname(self):
        return str(self._ds.ReferringPhysicianName).split('^')[1]

    @ dental_provider_firstname.setter
    def dental_provider_firstname(self, firstname):
        self._set_name("ReferringPhysicianName", firstname, 0)

    @ property
    def dental_provider_lastname(self):
        return str(self._ds.ReferringPhysicianName).split('^')[0]

    @ dental_provider_lastname.setter
    def dental_provider_lastname(self, lastname):
        self._set_name("ReferringPhysicianName", lastname, 1)

    @ property
    def timezone(self) -> datetime.timezone:
        """ Convert the TimezoneOffsetFromUTC to a Python datetime.timezone.

        :return: timezone from TimezoneOffsetFromUTC as a Python datetime.timezone object, or None if TimezoneOffsetFromUTC is not something that can be converted to an integer.
        """
        tz_str = self._ds.TimezoneOffsetFromUTC
        if tz_str is None or len(tz_str) < 5:
            return None
        
        try:
            # Extract hours and minutes from the string
            sign = -1 if tz_str[0] == '-' else 1
            hours = int(tz_str[1:3])
            minutes = int(tz_str[3:5])

            # Create a timedelta object
            td = datetime.timedelta(hours=sign * hours, minutes=sign * minutes)
            return datetime.timezone(td)
        except ValueError:
            return None

    @ timezone.setter
    def timezone(self, tz: datetime.timezone) -> None:
        ''' Set timezone of TimezoneOffsetFromUTC from a Python datetime.timezone object.

        If you know the timezone in string format, like "-0900", then you might be better off to set the `_ds` object directly.

        Example:

            from datetime import timezone, timedelta

            o = OrthodonticPhotograph()

            o.timezone = timezone(timedelta(hours=-9))

        Args:
            timezone: datetime.timezone
        Returns:
            None
        '''
        if tz:
            offset_seconds = tz.utcoffset(None).total_seconds()
            offset_hours = int(abs(offset_seconds) // 3600)
            offset_hours = copysign(offset_hours, offset_seconds)
            offset_minutes = int((offset_seconds % 3600) // 60)
            self._ds.TimezoneOffsetFromUTC = f"{offset_hours:+03.0f}{offset_minutes:02d}"
        else:
            self._ds.TimezoneOffsetFromUTC = None



    @ property
    def acquisition_datetime(self):
        return self._ds.AcquisitionDateTime

    @ acquisition_datetime.setter
    def acquisition_datetime(self, _acquisition_datetime: datetime.datetime):
        """
        Set Acquisition DateTime using local Time Zone.

        Also set Acquisition Date and Acquisition Time
        """
        if _acquisition_datetime.tzinfo is None and self.timezone:
            # If no timezone is present and a timezone is specified in the class, add it.
            _acquisition_datetime = _acquisition_datetime.replace(tzinfo=self.timezone)
        elif _acquisition_datetime.tzinfo is None:
            # If no timezone is present and no class timezone, use the current local timezone.
            _acquisition_datetime = _acquisition_datetime.astimezone()

        dtzs = _acquisition_datetime.strftime(
            f"{defaults.DATE_FORMAT}{defaults.TIME_FORMAT}%z")
        self._ds.AcquisitionDateTime = dtzs
        self._ds.AcquisitionDate = _acquisition_datetime.strftime(
            defaults.DATE_FORMAT)
        self._ds.AcquisitionTime = _acquisition_datetime.strftime(
            defaults.TIME_FORMAT)

    @ property
    def date_captured(self):
        ''' Date of image capture.

        Date and time are required if images is part of a Series in which the
        images are temporally related. This sounds like the case for
        orthodontic intraoral and extraoral photograph sets. return
        datetime.datetime.strptime(self.ds.ContentDate,
        defaults.DATE_FORMAT).date()
        '''
        return datetime.datetime.strptime(self._ds.ContentDate, defaults.DATE_FORMAT).date()

    @ date_captured.setter
    def date_captured(self, date_captured):
        # Date and time are required if images is part of a Series in which
        # the images are temporally related. This sounds like the case for orthodontic
        # intraoral and extraoral photograph sets.
        self._ds.ContentDate = date_captured.strftime(defaults.DATE_FORMAT)

    @ property
    def equipment_manufacturer(self):
        return self._ds.manufacturer

    @ equipment_manufacturer.setter
    def equipment_manufacturer(self, manufacturer):
        self._ds.Manufacturer = manufacturer

    def set_time_captured(self, time_captured):
        """ Set both AcquisitionDate/Time and ContentDate/Time to the same values.

        Sets in General Image Module:

        * Acquisition Date (0008,0022)
        * Content Date (0008,0023)
        * Acquisition DateTime (0008,002A)
        * Acquisition Time (0008,0032)
        * Content Time (0008,0033)
        """
        self.acquisition_datetime = time_captured  # This sets also AcquisitionDate and AcquisitionTime
        self._ds.ContentTime = self._ds.AcquisitionTime
        self._ds.ContentDate = self._ds.AcquisitionDate

    def save_implicit_little_endian(self, filename=None):
        if filename is None:
            filename = self.output_image_filename

        # Set the transfer syntax
        self._ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
        self._ds.is_little_endian = True
        self._ds.is_implicit_VR = True

        logging.debug(
            "Writing test file as Little Endian Implicit VR [{}]", filename)
        self._ds.save_as(filename, write_like_original=False)
        logging.info("File [{}] saved.".format(filename))

    def save_explicit_little_endian(self, filename=None):
        if filename is None:
            filename = self.output_image_filename
        self._ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        self._ds.is_little_endian = True
        self._ds.is_implicit_VR = False

        logging.debug(
            "Writing test file as Big Endian Explicit VR [{}]", filename)
        self._ds.save_as(filename, write_like_original=False)
        logging.info("File [{}] saved.", filename)

    def save_explicit_big_endian(self, filename=None):
        if filename is None:
            filename = self.output_image_filename
        # Write as a different transfer syntax XXX shouldn't need this but pydicom
        # 0.9.5 bug not recognizing transfer syntax
        self._ds.file_meta.TransferSyntaxUID = ExplicitVRBigEndian
        self._ds.is_little_endian = False
        self._ds.is_implicit_VR = False
        self._ds.save_as(filename, write_like_original=False)

    def load(self, filename):
        self._ds = pydicom_dcmread(filename)

    def print(self):
        print(self._ds)


class PhotographBase(DicomBase):
    """
    A.32.4 VL Photographic Image IOD
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_file_meta()
        self.file_meta.MediaStorageSOPClassUID = VLPhotographicImageStorage
        self._set_sop_common()
        self._set_general_series()
        self._set_vl_image()

    def _set_sop_common(self):
        super()._set_sop_common()
        self._ds.SOPClassUID = VLPhotographicImageStorage

    def _set_general_series(self):
        super()._set_general_series()
        self._ds.Modality = 'XC'

    def _set_vl_image(self):
        """
        Define if this is a scanned image, or an original capture.
        C.8.12.1.1.6 Image Type
            The Image Type Attribute identifies important image characteristics in a multiple valued Data Element. For Visible Light, Image Type is specialized as follows:

            Value 1 shall identify the Pixel Data Characteristics in accordance with Section C.7.6.1.1.2.

                Enumerated Values:

                ORIGINAL

                DERIVED

            Value 2 shall identify the Patient Examination Characteristics in accordance with Section C.7.6.1.1.2.

                Enumerated Values:

                PRIMARY

                SECONDARY

            Value 3 may be absent, but if present shall identify the members of a stereo pair, in which case Referenced Image Sequence (0008,1140) is used to identify the other member of the pair.

                Enumerated Values:

                STEREO L
                Image is the left image (relative to the observer's left) of a stereo pair acquisition

                STEREO R
                Image is the right image (relative to the observer's right) of a stereo pair acquisition

            Other Values are implementation specific (optional).
        """
        self._ds.ImageType = ['ORIGINAL', 'PRIMARY']

        # Specifies whether an Image has undergone lossy compression (at a
        # point in its lifetime).
        self._ds.LossyImageCompression = ''

    def is_digitized_image(self):
        """
        A digitized image is considered as secondary capture for DICOM. As an example, if the original photograph was taken with an analog camera, and the negative, positive or print was then scanned, the scanned image should be recorded in DICOM as secondary, and this method should be used.
        See C.7.6.1.1.2 Image Type
        """
        self._ds.ImageType[1] = 'SECONDARY'

    def is_primary_image(self):
        """ A primary image is one that was generated by the device that was
        used to capture the original photograph from the patient.

        As an example, if the original photograph was taken with a digital
        camera, that image should be recorded in DICOM using this method. See
        C.7.6.1.1.2 Image Type
        """
        self._ds.ImageType[1] = 'PRIMARY'

    def is_original_image(self):
        self._ds.ImageType[0] = 'ORIGINAL'

    def is_derived_image(self):
        """ A derived image is a manipulated image.

        It's not the original anymore, it's been most likely enhanced with
        some calculation or filters.
        """
        self._ds.ImageType[0] = 'DERIVED'

    def lossy_compression(self, lossy):
        if lossy == True:
            self._ds.LossyImageCompression = '01'
        elif lossy == False:
            self._ds.LossyImageCompression = '00'

    def _set_image_raw_data(self, filename=None):
        """ Sets general Image Module Data and Metadata

            Image Pixel M
            Pixel Data (7FE0,0010) for this image. The order of pixels encoded for each image plane is left to right, top to bottom, i.e., the upper left pixel (labeled 1,1) is encoded first followed by the remainder of row 1, followed by the first pixel of row 2 (labeled 2,1) then the remainder of row 2 and so on.
            It's Planar Configuration which defines how the values are stored in the PixelData, which is defined to be 0, in this case.
            C.7.6.3.1.3 Planar Configuration
            Planar Configuration (0028,0006) indicates whether the color pixel data are encoded color-by-plane or color-by-pixel. This Attribute shall be present if Samples per Pixel (0028,0002) has a value greater than 1. It shall not be present otherwise.

            Enumerated Values:

            0
            The sample values for the first pixel are followed by the sample values for the second pixel, etc. For RGB images, this means the order of the pixel values encoded shall be R1, G1, B1, R2, G2, B2, …, etc.
        """
        filename = filename or self.input_image_filename
        with Image.open(filename) as im:

            # Note

            # self._ds.Rows = im.size[1]
            # self._ds.Columns = im.size[0]
            self._ds.Rows = im.height
            self._ds.Columns = im.width
            self._ds.PixelRepresentation = 0x0
            # (1-bit pixels, black and white, stored with one pixel per byte)
            if im.mode == '1':
                self._ds.SamplesPerPixel = 1
                try:
                    del self._ds.PlanarConfiguration
                except AttributeError:
                    pass
                self._ds.BitsStored = 1
                self._ds.HighBit = 0
                self._ds.PhotometricInterpretation = 'MONOCHROME2'
                # @TODO: Not sure if this works
                # Got this from https://stackoverflow.com/questions/5602155/numpy-boolean-array-with-1-bit-entries
                npa = numpy.array(im.getdata(), dtype=numpy.bool)
                self._ds.PixelData = numpy.packbits(npa, axis=None).tobytes()
            elif im.mode == 'L':  # (8-bit pixels, black and white)
                self._ds.SamplesPerPixel = 1
                try:
                    del self._ds.PlanarConfiguration
                except AttributeError:
                    pass
                self._ds.BitsAllocated = 8
                self._ds.BitsStored = 8
                self._ds.HighBit = 7
                self._ds.PhotometricInterpretation = 'MONOCHROME2'
                self._ds.PixelData = numpy.array(
                    im.getdata(), dtype=numpy.uint8).tobytes()
            # (8-bit pixels, mapped to any other mode using a color palette)
            elif im.mode == 'P':
                print(
                    "ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError

                # self.ds.SamplesPerPixel = 1
                # self.ds.BitsAllocated = 8
                # self.ds.BitsStored = 8
                # self.ds.HighBit = 7
                # self.ds.PhotometricInterpretation = 'PALETTE COLOR'
            elif im.mode == 'RGB':  # (3x8-bit pixels, true color)
                self._ds.SamplesPerPixel = 3
                # Planar Configuration (0028,0006) is not meaningful when a compression Transfer Syntax is used that involves reorganization of sample components in the compressed bit stream. In such cases, since the Attribute is required to be present, then an appropriate value to use may be specified in the description of the Transfer Syntax in PS3.5, though in all likelihood the value of the Attribute will be ignored by the receiving implementation.
                self._ds.PlanarConfiguration = 0
                self._ds.BitsAllocated = 8
                self._ds.BitsStored = 8
                self._ds.HighBit = 7
                self._ds.PhotometricInterpretation = 'RGB'
                self._ds.PixelData = numpy.array(im.getdata(), dtype=numpy.uint8)[
                    :, :3].tobytes()
            # (4x8-bit pixels, true color with transparency mask)
            elif im.mode == 'RGBA':
                print(
                    "ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
                # self.ds.SamplesPerPixel = 4
                # self.ds.PlanarConfiguration = 0
                # self.ds.BitsAllocated = 8
                # self.ds.BitsStored = 8
                # self.ds.HighBit = 7
                # self.ds.PhotometricInterpretation = 'ARGB'
            elif im.mode == 'CMYK':  # (4x8-bit pixels, color separation)
                print(
                    "ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
                # self.ds.SamplesPerPixel = 4
                # self.ds.PlanarConfiguration = 0
                # self.ds.BitsAllocated = 8
                # self.ds.BitsStored = 8
                # self.ds.HighBit = 7
                # self.ds.PhotometricInterpretation = 'CMYK'
            # (3x8-bit pixels, color video format) Note that this refers to the JPEG, and not the ITU-R BT.2020, standard
            elif im.mode == 'YCbCr':
                print(
                    "ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
                # self.ds.SamplesPerPixel = 3
                # self.ds.PlanarConfiguration = 0
                # self.ds.BitsAllocated = 8
                # self.ds.BitsStored = 8
                # self.ds.HighBit = 7
                # self.ds.PhotometricInterpretation = 'YBR_FULL'
            elif im.mode == 'LAB':  # (3x8-bit pixels, the L*a*b color space)
                print(
                    "ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
            # (3x8-bit pixels, Hue, Saturation, Value color space)
            elif im.mode == 'HSV':
                print(
                    "ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
            elif im.mode == 'I':  # (32-bit signed integer pixels)
                print(
                    "ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
            elif im.mode == 'F':  # (32-bit floating point pixels)
                print(
                    "ERROR: mode [{}] is not yet implemented.".format(im.mode))
                raise NotImplementedError
        self._ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
        self._ds.is_little_endian = True
        self._ds.is_implicit_VR = False

        return filename

    def _set_image_jpeg2000_data(self, filename=None):
        """ Set Image Data for JPEG2000 Images.

        Encapsulates a JPEG2000 as it is, without touching anything.
        """
        filename = filename or self.input_image_filename
        # self._set_image_raw_data(filename=filename)
        with Image.open(filename) as im:
            self._ds.Rows = im.height
            self._ds.Columns = im.width
            with open(file=filename, mode="rb") as image_file:
                self._ds.PixelData = encapsulate(
                    [image_file.read()])  # needs to be an array

        self._ds['PixelData'].is_undefined_length = True

        # Values as defined in Part 5 Sect 8.2.4
        # https://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_8.2.4.html
        self._ds.PhotometricInterpretation = 'RGB'
        self._ds.SamplesPerPixel = 3
        self._ds.PlanarConfiguration = 0
        self._ds.PixelRepresentation = 0
        self._ds.BitsAllocated = 8
        self._ds.BitsStored = 8
        self._ds.HighBit = 7

        self._ds.LossyImageCompressionMethod = 'ISO_15444_1'  # The JPEG-2000 Standard

        self._ds.file_meta.TransferSyntaxUID = JPEG2000
        self._ds.is_little_endian = True
        self._ds.is_implicit_VR = False

        self.lossy_compression(False)
        # self._ds.compress(RLELossless)
        return filename

    def _set_image_jpeg_data(self, filename=None, recompress_quality=None):
        """ Set Image Data for JPG Images.

        If a lossy JPG image is obtained from the camera (non-ideal), then we should just store it as such. Storing it as raw is not reccommende because it would deceiving (unless one adds all the secondary capture tags), becuase the image would have been compressed in the first place, but then stored uncompressed, so data would be lost, without this being recorded anywhere. And takes up a lot more space.

        Some cameras, like the Nikon D5600 will actually save MPO images, which will not support the quality argument and throw a ValueError.

        If the MPO image contains multiple frames, they are expanded in multiframe DICOM encapsulation, as described here: https://stackoverflow.com/questions/58518357/how-to-create-jpeg-compressed-dicom-dataset-using-pydicom Not sure there is a usecase for it. 

        Quality of 98

        """
        filename = filename or self.input_image_filename
        with Image.open(filename) as im:
            logging.info(f"Found format {im.format} for {filename} image")
            self._ds.Rows = im.height
            self._ds.Columns = im.width

            if recompress_quality is None:
                with open(file=filename, mode="rb") as image_file:
                    self._ds.PixelData = encapsulate(
                        [image_file.read()])  # needs to be an array
            else:
                with io.BytesIO() as output:
                    im.save(output, format='jpeg', quality=recompress_quality)
                    self._ds.PixelData = encapsulate(
                        [output.getvalue()])  # needs to be an array

        # self._ds['PixelData'].is_undefined_length = True

        # Values as defined in Part 5 Sect 8.2.1
        # https://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_8.2.html#sect_8.2.1
        # self._ds.PhotometricInterpretation = 'RGB'
        self._ds.PhotometricInterpretation = 'YBR_FULL_422'
        self._ds.SamplesPerPixel = 3
        self._ds.PlanarConfiguration = 0
        self._ds.PixelRepresentation = 0
        self._ds.BitsAllocated = 8
        self._ds.BitsStored = 8
        self._ds.HighBit = 7

        self._ds.LossyImageCompressionRatio = 10
        self._ds.LossyImageCompressionMethod = 'ISO_10918_1'  # The JPEG Standard

        self._ds.file_meta.TransferSyntaxUID = JPEGExtended12Bit
        self._ds.is_little_endian = True
        self._ds.is_implicit_VR = False

        self.lossy_compression(True)
        return filename

    def set_image(self, filename=None):
        filename = filename or self.input_image_filename
        with Image.open(filename) as img:
            file_type = img.format
        if file_type in ('JPEG', 'MPO'):
            self._set_image_jpeg_data(filename=filename)
        elif file_type in ('JPEG2000'):
            self._set_image_jpeg2000_data(filename=filename)
        else:
            # DICOM only supports encapsulation for JPEG. Everything else needs to be decoded and re-encoded as raw.
            self._set_image_raw_data(filename=filename)
