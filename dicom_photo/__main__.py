"""

"""

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import dicom_photo.defaults as defaults
import dicom_photo.m_orthodontic_photograph
import dicom_photo.controller
import sys, os
import logging

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

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
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
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
            metavar='<filename>',
        )
        parser.add_argument(
            "-t", "--image-type",
            dest="image_type",  
            help="What type of image this is",
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
            help="path of file to convert to DICOM",
            metavar='<filename>',
        )


        # Process arguments
        args = parser.parse_args()
        if args.verbose is True:
            args.log_level = logging.DEBUG

        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s: %(message)s',
                    level=args.log_level)

        c = dicom_photo.controller.SimpleController(args)

        if args.validate is True:
            c.validate_dicom_file(args.input_filename)
        else:
            c.convert_image_to_dicom_photograph(
                image_type=args.image_type,
                input_image_filename=args.input_filename,
                output_image_filename=args.output_filename)
            c.photo.print()


    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        exit(120)
        return 0

if __name__ == "__main__":
    exit(main())
