from os import walk
from os.path import splitext, join

import os,sys

"""
lcgRecursiveCopy.py
-------------------

Enables people to recursively copy a local directory to a Tier2/3 storage area (operation currently not supported by any grid CMS utility, apparently)

Author: Pietro Vischia, pietro.vischia@gmail.com
"""


# Python 2.7: from argparse import ArgumentParser
from optparse import OptionParser
# Python 2.7: parser = OptionParser(description='This script copies recursively a local directory to a Tier2/3 (for now, only T2_PT_NCG_Lisbon)')
parser = OptionParser(description='This script copies recursively a local directory to a Tier2/3 (for now, only T2_PT_NCG_Lisbon)')

parser.add_option("-u", "--username", dest="username", help="username (will be used for creating the final path in the storage area)")
parser.add_option("-i", "--input",    dest="input",    help="source directory (absolute local path)")
parser.add_option("-o", "--output",   dest="output",   help='destination directory: it is assumed to be specified as a relative path starting from AFTER /cmst3/store/user/, meaning that "-u bulabula -o storage/testes4" will become "srm://srm01.ncg.ingrid.pt:8444/srm/managerv2?SFN=/cmst3/store/user/bulabula/storage/testes4/"')

# Python 2.7: args = parser.parse_args()
(options, args) = parser.parse_args()
if not options.username:
    parser.print_help()
    parser.error("No username provided")
if not options.input:
    parser.print_help()
    parser.error("No input directory provided")
if not options.output:
    parser.print_help()
    parser.error("No output directory provided")


def selectFiles(root, files, path):

    selectedFiles = []
    selectedFilesWithPath = []
    for file in files:
        #do concatenation here to get full path 
        fullPath = join(root, file)

        
        ### Extend this to include configurable desired file format/formats to include/exclude from the copy  
        #        ext = splitext(file)[1]
        #        if ext == ".py":
        #            selected_files.append(full_path)
        selectedFilesWithPath.append(fullPath)
        print fullPath
        print "PATH IS " + path
        fullPath = fullPath.replace(path,'') 
        print fullPath
        selectedFiles.append(fullPath)
    return {'files': selectedFiles, 'filesWithPath': selectedFilesWithPath }

def buildRecursiveDirTree(path):
    """
    path    -    where to begin folder scan
    """
    selectedFiles = []
    selectedFilesWithPath = []
    for root, dirs, files in walk(path):
        result = selectFiles(root,files,path)
        selectedFiles += result['files']
        selectedFilesWithPath += result['filesWithPath']

    return selectedFiles, selectedFilesWithPath

def lcgCopyDirTree(username, relDestPath, files, filesWithPath):
    """
    Invoke lcg-cp to copy files to the desired Tier2
    """
    print "Now copying"
    tier="srm://srm01.ncg.ingrid.pt:8444/srm/managerv2?SFN=/cmst3/store/user/"
    destPath=tier+username+"/"+relDestPath

    for i in range(len(files)):
        cmd='lcg-cp --verbose -b -D srmv2 file://'+filesWithPath[i]+' "'+destPath+'/'+files[i]+'" >> LOG'+' &'
        os.system(cmd) 
        
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
print "Source directory: " + options.input
print "Destination directory: " + options.output

listFiles = []
listFilesWithPath = []
listFiles, listFilesWithPath=buildRecursiveDirTree(options.input)
print listFilesWithPath
lcgCopyDirTree(options.username,options.output,listFiles,listFilesWithPath)
