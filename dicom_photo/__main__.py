""" Command Line entry point.

"""

import sys
import logging
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import dicom_photo.defaults as defaults
import dicom_photo.controller as controller
import pkg_resources
import textwrap
import csv
from prettytable import from_csv, PrettyTable

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
    image_types_filename = pkg_resources.resource_filename(
        'dicom_photo.resources', 'image_types.csv')
    logging.debug("Image type filenames is: {}".format(image_types_filename))
    HEADER1 = 'Type'
    HEADER2 = 'Abbreviated'
    HEADER3 = 'Full Meaning'
    with open(image_types_filename) as image_types_csvfile:
        reader = csv.reader(image_types_csvfile)
        image_types_table = PrettyTable([HEADER1,HEADER2,HEADER3])
        for row in reader:
            wrapped_meaning = textwrap.wrap(row[2], 47)
            image_types_table.add_row([row[0],
                                      row[1],
                                      wrapped_meaning[0]])
            for subseq in wrapped_meaning[1:]:
                image_types_table.add_row(['','','  {}'.format(subseq)])
        # image_types_table = from_csv(image_types_csvfile)

    image_types_table.align[HEADER2] = "l"
    image_types_table.align[HEADER3] = "l"
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

  Created by Toni Magni on {creation_date}.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

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
            help="Configure the logging level. Available values: debug, info, warning, error, critical.",
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
        # parser.add_argument(
        #     "-l", "--list-image-types",
        #     dest="list_image_types",
        #     action="store_true",
        #     help="Prints a list of allowed image types for --image-type",
        # )
        parser.add_argument(
            "-t", "--image-type",
            dest="image_type",
            help="Type of image using the abbreviations defined in ADA SCDI \
            TR-1107. Use {} to get a list of allowed image \
            types. [default: %(default)s]".format(LIST_IMAGE_TYPES),
            default='EV01',
            metavar='<filename>',
        )
        parser.add_argument(
            "--validate",
            dest="validate",
            action="store_true",
            help="Validate DICOM File",
        )
        parser.add_argument(
            dest="input_filename",
            help="path of file of CSV file with metadata and filename of file to convert to DICOM",
            metavar='<filename>',
        )

        # Process arguments
        args = parser.parse_args()
        if args.verbose is True:
            args.log_level = logging.DEBUG

        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                            level=args.log_level)

        if args.input_filename == LIST_IMAGE_TYPES:
            print_image_types()
            sys.exit(0)

        c = controller.SimpleController(args)

        if args.validate is True:
            c.validate_dicom_file(args.input_filename)
        elif args.input_filename.lower().endswith('.csv'):
            c.bulk_convert_from_csv(args.input_filename)
        else:
            c.convert_image_to_dicom_photograph({
                'image_type': 'args.image_type',
                'image_filename': 'args.input_filename',
                'output_image_filename': 'args.output_filename'})
            c.photo.print()

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        exit(120)
        return 0


if __name__ == "__main__":
    exit(main())
