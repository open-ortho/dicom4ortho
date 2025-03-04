""" Command Line entry point.

"""

import sys
import logging
import textwrap
import csv
import os
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import importlib.resources as importlib_resources
from prettytable import PrettyTable

from dicom4ortho import logger
import dicom4ortho.config as config
import dicom4ortho.controller as controller
from dicom4ortho.utils import generate_dicom_uid

LIST_IMAGE_TYPES = 'list-image-types'


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''

    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg

def setup_logging(log_level):
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s.%(funcName)s: %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def print_image_types():
    image_types_filename = importlib_resources.files('dicom4ortho.resources') / 'image_types.csv'
    logger.debug("Image type filenames is: %s",image_types_filename)
    header1 = 'Type'
    header2 = 'Abbreviated'
    header3 = 'Full Meaning'
    with importlib_resources.as_file(image_types_filename) as image_types_csvfile:
        reader = csv.reader(image_types_csvfile)
        image_types_table = PrettyTable([header1, header2, header3])
        for row in reader:
            wrapped_meaning = textwrap.wrap(row[2], 47)
            image_types_table.add_row([row[0],
                                       row[1],
                                       wrapped_meaning[0]])
            for subseq in wrapped_meaning[1:]:
                image_types_table.add_row(['', '', '  {}'.format(subseq)])
        # image_types_table = from_csv(image_types_csvfile)

    image_types_table.align[header2] = "l"
    image_types_table.align[header3] = "l"
    print(image_types_table)


def main(argv=None):
    '''Command line options.'''
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_version = "v%s" % config.VERSION
    program_version_message = '%%(prog)s %s' % (program_version)
    program_license = '''{short_description}

USAGE
'''.format(
        short_description=config.__short_description__,
        creation_date=config.__creation_date__)

    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument(
            "-v", "--verbose",
            dest="verbose",
            action="store_true",
            help="set verbosity level [default: %(default)s]",
        )
        parser.add_argument(
            "--log-level",
            dest="log_level",
            default=logging.INFO,
            type=lambda x: getattr(logging, x.upper()),
            help="Configure the logging level. Available values: debug, info, \
            warning, error, critical.",
        )
        parser.add_argument(
            '-V', '--version',
            action='version',
            version=program_version_message,
        )
        parser.add_argument(
            "--url-codes",
            dest="url_codes",
            help="URL for location of codes.csv file. Use to override internal ones.",
            default=None,
            metavar='<filename>',
        )
        parser.add_argument(
            "--url-views",
            dest="url_views",
            help="URL for location of views.csv file. Use to override internal ones.",
            default=None,
            metavar='<filename>',
        )
        parser.add_argument(
            "-o", "--output-filename",
            dest="output_filename",
            help="Where to store the DICOM file. ",
            default=None,
            metavar='<filename>',
        )
        parser.add_argument(
            "-t", "--image-type",
            dest="image_type",
            help="Type of image using the abbreviations defined in DENT-OIP. \
            Use {} to get a list of allowed image \
            types. [default: %(default)s]".format(LIST_IMAGE_TYPES),
            default='EV01',
            metavar='<image_type>',
        )
        parser.add_argument(
            "--validate",
            dest="validate",
            action="store_true",
            help="Validate DICOM File",
        )
        parser.add_argument(
            dest="input_filename",
            help="path of file or CSV file with metadata and filename of files \
            to convert to DICOM",
            metavar='<filename>',
        )

        # Process arguments
        args = parser.parse_args(argv[1:])
        if args.verbose is True:
            args.log_level = logging.DEBUG
        else:
            args.log_level = logging.INFO

        setup_logging(args.log_level)

        logger.debug("passed arguments: %s",argv)
        for k,v in sorted(vars(args).items()):
            logger.debug("%s: %s",k,v)

        if args.input_filename == LIST_IMAGE_TYPES:
            print_image_types()
            return 0

        if not os.path.isfile(args.input_filename):
            logger.error("Cannot locate file %s:",args.input_filename)
            return 1

        c = controller.OrthodonticController(
            url_codes=args.url_codes,
            url_views=args.url_views)

        if args.validate is True:
            c.validate_dicom_file(args.input_filename)
            return 0
        elif args.input_filename.lower().endswith('.csv'):
            c.bulk_convert_from_csv(args.input_filename)
            return 0
        else:
            c.convert_image_to_dicom4orthograph_and_save({
                'image_type': args.image_type,
                'input_image_filename': args.input_filename,
                'output_image_filename': args.output_filename})
            c.photo.print()
            return 0

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 120


def generate_uid():
    print(generate_dicom_uid())

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
