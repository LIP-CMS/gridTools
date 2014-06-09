import os
from os import walk
from os.path import splitext, join
import hashlib
import subprocess

def hashFile(filename, blocksize=65536):
    # hash = hashlib.md5()
    hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), ""):
            hash.update(block)
    return hash.hexdigest()



    
def selectFiles(root, files, path, options):

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
        if(options.debug):
            print fullPath
            print "PATH IS " + path
        fullPath = fullPath.replace(path,'') 
        if(options.debug):
            print fullPath
        selectedFiles.append(fullPath)
    return {'files': selectedFiles, 'filesWithPath': selectedFilesWithPath }


def buildRecursiveDirTree(path, options):
    """
    path    -    where to begin folder scan
    """
    
    selectedFiles = []
    selectedFilesWithPath = []

    if options.remove:
        lustrePath="/lustre/ncg.ingrid.pt/cmst3/store/user/"+options.username+"/"+path
        if(options.debug):
            print "New path: " + lustrePath
        path=lustrePath
        
    for root, dirs, files in walk(path):
        result = selectFiles(root,files,path, options)
        selectedFiles += result['files']
        selectedFilesWithPath += result['filesWithPath']

    return selectedFiles, selectedFilesWithPath


def lcgOperateOnDirTree(username, relDestPath, files, filesWithPath, options):
    """
    Invoke lcg-cp to copy files to the desired Tier2
    """
    if(options.debug):
        print "Now copying"
    tier="srm://srm01.ncg.ingrid.pt:8444/srm/managerv2?SFN=/cmst3/store/user/"
    destPath=tier+username+"/"+relDestPath

    os.system('rm LOG')
    os.system('touch LOG')
    for i in range(len(files)):
        if not options.remove:    
            cmd='lcg-cp --checksum --verbose -b -D srmv2 file://'+filesWithPath[i]+' "'+destPath+'/'+files[i]+'"'
            print 'CMD=' + cmd
            if options.dryrun:
                print cmd
            else:
                os.system(cmd) 
                m1=0
                if os.path.isfile(filesWithPath[i]):
                    m1 = hashFile(filesWithPath[i])
                fileToHash='/lustre/ncg.ingrid.pt/cmst3/store/user/'+username+'/'+relDestPath+'/'+files[i]
                m2=0
                if os.path.isfile(fileToHash):
                    m2 = hashFile(fileToHash)
                if m1 != m2:
                    print 'ERROR: file ' + relDestPath+'/'+files[i] + ' has been copied uncorrectly (sha256 hashes diverge), m1=' + str(m1) + ', m2=' + str(m2)
                else:
                    print 'OK: file ' + relDestPath+'/'+files[i] + ' has been copied successfully (sha256 hashes are equal), m1=' + str(m1) + ', m2=' + str(m2)
                    #sys.stdout.flush()
        else:
            filesWithPath[i] = filesWithPath[i].replace("/lustre/ncg.ingrid.pt/cmst3/store/user/",tier)
            if options.debug:
                print "File that will be removed: " + filesWithPath[i]
            cmd='lcg-del --verbose -b -D srmv2 "'+filesWithPath[i]+'" >> LOG'+' &'
            if options.dryrun:
                print cmd
                #print os.system("whoami")
                meis = subprocess.Popen("whoami")
                #print meis
                # Python 2.7: subprocess.check_output(["whoami",""])
            else:
                print cmd
