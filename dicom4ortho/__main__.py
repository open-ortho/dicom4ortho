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

import dicom4ortho.defaults as defaults
import dicom4ortho.controller as controller

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


def print_image_types():
    image_types_filename = importlib_resources.files('dicom4ortho.resources') / 'image_types.csv'
    logging.debug("Image type filenames is: {}".format(image_types_filename))
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

    program_version = "v%s" % defaults.VERSION
    program_version_message = '%%(prog)s %s' % (program_version)
    program_license = '''{short_description}

USAGE
'''.format(
        short_description=defaults.__short_description__,
        creation_date=defaults.__creation_date__)

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
            "-o", "--output-filename",
            dest="output_filename",
            help="Where to store the DICOM file. ",
            default=None,
            metavar='<filename>',
        )
        parser.add_argument(
            "-t", "--image-type",
            dest="image_type",
            help="Type of image using the abbreviations defined in ADA SCDI \
            TR-1107. Use {} to get a list of allowed image \
            types. [default: %(default)s]".format(LIST_IMAGE_TYPES),
            default='EV01',
            metavar='<image_type>',
        )
        parser.add_argument(
            "--teeth",
            dest="teeth",
            nargs="*",
            help="Add this tooth to image. Tooth should be clearly visible. \
            Use ISO tooth numbering. Add as many as necessary, divided by a \
            space, like: '--teeth 18 17 16'.",
        )
        parser.add_argument(
            "--add-max-allowed-teeth",
            dest="add_max_allowed_teeth",
            action="store_true",
            help="Adds the maximum allowed teeth for each image type. Assumes \
            adult patient with all teeth present and clearly visible for the \
            specified image type.",
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

        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                            level=args.log_level)

        logging.debug("passed arguments: {}".format(argv))
        for k,v in sorted(vars(args).items()):
            logging.debug("{0}: {1}".format(k,v))

        if args.input_filename == LIST_IMAGE_TYPES:
            print_image_types()
            return 0

        if not os.path.isfile(args.input_filename):
            logging.error("Cannot locate file {}:".format(args.input_filename))
            return 1

        c = controller.SimpleController(args)
        if args.add_max_allowed_teeth:
            teeth = defaults.ADD_MAX_ALLOWED_TEETH
        elif args.teeth:
            teeth = args.teeth
        else:
            teeth = []

        if args.validate is True:
            c.validate_dicom_file(args.input_filename)
            return 0
        elif args.input_filename.lower().endswith('.csv'):
            c.bulk_convert_from_csv(args.input_filename, teeth=teeth)
            return 0
        else:
            c.convert_image_to_dicom4orthograph_and_save({
                'image_type': args.image_type,
                'input_image_filename': args.input_filename,
                'teeth': teeth,
                'output_image_filename': args.output_filename})
            c.photo.print()
            return 0

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 120


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
