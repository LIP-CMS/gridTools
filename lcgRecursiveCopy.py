from os import walk
from os.path import splitext, join

"""
lcgRecursiveCopy.py
-------------------

Enables people to recursively copy a local directory to a Tier2/3 storage area (operation currently not supported by any grid CMS utility, apparently)

Author: Pietro Vischia, pietro.vischia@gmail.com
"""


def selectFiles(root, files):

    selectedFiles = []

    for file in files:
        #do concatenation here to get full path 
        fullPath = join(root, file)

        
        ### Extend this to include configurable desired file format/formats to include/exclude from the copy  
        #        ext = splitext(file)[1]
        #        if ext == ".py":
        #            selected_files.append(full_path)
        selectedFiles.append(fullPath)

    return selectedFiles

def buildRecursiveDirTree(path):
    """
    path    -    where to begin folder scan
    """
    selectedFiles = []

    for root, dirs, files in walk(path):
        selectedFiles += selectFiles(root, files)

    return selectedFiles

def lcgCopyDirTree(files):
    """
    Invoke lcg-cp to copy files to the desired Tier2
    """
    print "Now copying"
    username="vischia"
    relDestPath="storage/test"
    tier="srm://srm01.ncg.ingrid.pt:8444/srm/managerv2?SFN=/cmst3/store/user/"
    destPath=tier+username+"/"+relDestPath

    for f in files:
        cmd='lcg-cp --verbose -b -D srmv2 file://'+f+' "'+destPath+'" >> LOG'+' &'
        print cmd
        #        os.system('lcg-cp --verbose -b -D srmv2 file://"'+f+' "'+destPath+'" >> LOG'+' &') 


# Main

myDir="/var/log/"
print "List directory " + myDir
print "======================================================="
listing=buildRecursiveDirTree(myDir)
print listing
lcgCopyDirTree(listing)
