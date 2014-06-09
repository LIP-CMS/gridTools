import os
import sys


"""
lcgRecursiveDel.py
-------------------

Enables people to recursively delete a directory from a Tier2/3 storage area (operation currently not supported by any grid CMS utility, apparently)

Author: Pietro Vischia, pietro.vischia@gmail.com
"""

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# Python 2.7: from argparse import ArgumentParser
from optparse import OptionParser,OptionGroup
# Python 2.7: parser = OptionParser(description='This script copies recursively a local directory to a Tier2/3 (for now, only T2_PT_NCG_Lisbon)')
parser = OptionParser(description='This script deletes recursively a directory from a Tier2/3 (for now, only T2_PT_NCG_Lisbon). CHECK WITH A DRY RUN BEFORE DELETING THE FILES. IT IS FULLY YOUR RESPONSIBILITY')

commonOpts = OptionGroup(parser, "Common options", "Options common to recursive copy and deletion")
commonOpts.add_option("-u", "--username", dest="username", help="username (will be used for creating the final path in the storage area)")
commonOpts.add_option("-d", "--dryRun",   dest="dryrun",   help='Only show the commands which will be executed', action="store_true")
commonOpts.add_option("-v", "--verbose",  dest="debug",    help='Activate debug mode (verbose printing)',       action="store_true")
parser.add_option_group(commonOpts)

copyOpts = OptionGroup(parser, "Copy options", "Options active only for recursive COPY")                  
copyOpts.add_option("-i", "--input",    dest="input",    help="source directory (absolute local path)")
copyOpts.add_option("-o", "--output",   dest="output",   help='destination directory: it is assumed to be specified as a relative path starting from AFTER /cmst3/store/user/, meaning that "-u bulabula -o storage/testes4" will become "srm://srm01.ncg.ingrid.pt:8444/srm/managerv2?SFN=/cmst3/store/user/bulabula/storage/testes4/"')
parser.add_option_group(copyOpts)

deletionOpts = OptionGroup(parser, "Deletion options", "Options active only for recursive DELETION")
deletionOpts.add_option("-r", "--remove",   dest="remove",   help='Remove the directory object of the -o option', action="store_true")
parser.add_option_group(deletionOpts)


# Python 2.7: args = parser.parse_args()
(options, args) = parser.parse_args()
if not options.remove:
    parser.print_help()
    parser.error("You can't remove files without calling explicitly the option --remove")
if not options.username:
    parser.print_help()
    parser.error("No username provided")
if not options.output:
    parser.print_help()
    parser.error("Directory to be removed not provided")
if not options.dryrun:
    print "You did not enable dry run: you are on your own, bitch!"
else:
    print "This is a dry run"

from tools import *

options.input = ""
   
# Main
if len(sys.argv) == 0:
    print "Usage: " + sys.argv[0] + " /path/to/input/directory " + " relative/path/to/Destination"
    print "Warning: destination is assumed to be specified from after /cmst3/store/user/"
    
if sys.argv[1] == "--help":
    print "Usage: " + sys.argv[0] + " /path/to/input/directory " + " relative/path/to/Destination"
    print "Warning: destination is assumed to be specified from after /cmst3/store/user/"

# Python 2.7
#inDir =args.input
#outDir=args.output

print "Username: " + options.username
if not options.remove:
    print "Source directory: " + options.input
    print "Destination directory: " + options.output
else:
    print "Directory that will be removed: " + options.output
    
listFiles = []
listFilesWithPath = []
if not options.remove:
    listFiles, listFilesWithPath=buildRecursiveDirTree(options.input, options)
else:
    listFiles, listFilesWithPath=buildRecursiveDirTree(options.output, options)
# print listFilesWithPath
lcgOperateOnDirTree(options.username,options.output,listFiles,listFilesWithPath,options)
