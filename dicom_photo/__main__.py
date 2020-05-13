"""

"""

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import dicom-vl-photographic-image.defaults

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, BRANCHNAME)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Toni Magni on %s.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", 
                            dest="verbose", 
                            action="store_true", 
                            help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', 
                            action='version', 
                            version=program_version_message)
#         parser.add_argument("-u", "--username",
#                             dest="username",  
#                             help="specify the tops staff's username (eg.: msanchez)",
#                             metavar="<username>")
        parser.add_argument("-o", "--output-filename",
                            dest="output_filename",  
                            help="Where to store the DICOM file. ",
                            metavar='<key>')
#         parser.add_argument("-b", "--backup",
#                             dest="backup_path",  
#                             help="specify the path to the topsBackup to restore",
#                             metavar='<path>')
#         parser.add_argument("-s", "--snapshot",
#                             dest="snapshot_id",  
#                             help="specify the topsBackup's snapshot ID to restore",
#                             metavar='<id>')
#         parser.add_argument("-c", "--clear-config", 
#                             dest="clear_config", 
#                             action="store_true", 
#                             help="remove the configuration file [default: %(default)s]")
# #         parser.add_argument("-a", "--staging", 
# #                             dest="staging", 
# #                             action="store_true", 
# #                             help="run the staging version, instead of the production version [default: %(default)s]")
#         parser.add_argument("--no-restore", 
#                             dest="no_restore", 
#                             action="store_true", 
#                             help="skip database restore [default: %(default)s]")
#         parser.add_argument("--hpc", 
#                             dest="hpc", 
#                             action="store_true", 
#                             help="High Performance Cloud server, instead of onsite server [default: %(default)s]")
#         parser.add_argument("--tempserver", 
#                             dest="tempserver", 
#                             action="store_true",
# #                             default=None,
#                             help="destination server is a temp server [default: %(default)s]")
#         parser.add_argument(dest="action", 
#                             help="specify what to do: transfer|install|printhw")


        # Process arguments
        args = parser.parse_args()

        global ARGS
        global BASEURL
        ARGS = {}
        ARGS['verbose'] = args.verbose # need to set this for args_to_dict
        ARGS            = args_to_dict(args)
        if ARGS['verbose']:
            log_debug("Verbose mode on")

        if ARGS['clear_config'] == True:
            log_debug('clearing configuration file')
            if os.path.isfile(CONFIG):
                os.remove(CONFIG)

#         if ARGS['staging'] == True:
#             BASEURL = '{}/staging'.format(BASEURL)
#         else:
#             BASEURL = '{}/production'.format(BASEURL)
         

        if ARGS['action'] == 'transfer':
            transfer_topsServer()
        elif ARGS['action'] == 'printhw':
            print(get_Mac_Hardware_String())
        elif ARGS['action'] == 'install':
            print("Action [install] not yet implemented.")
        else:
            log_err('Unrecognized action [{}].'.format(ARGS['action']))
               

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        exit_all(120)
        return 0

if __name__ == "__main__":
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'tops-server-setup.topsServer_transfer_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        exit_all(0)
    exit_all(main())
