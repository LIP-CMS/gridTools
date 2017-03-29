
import os,subprocess

verbose = False

def listDir(path):
  p = subprocess.Popen(['ls',path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = p.communicate()
  return out.split()

def recursiveConsolidate(inDir, tierPath, user, basePath, dryRun=True):
  correctlyCopied = True
  nubs = listDir(inDir)

  for nub in nubs:
    if verbose:
      print "Checking nub", nub

    if os.path.isfile(inDir+"/"+nub):
      if verbose:
        print "  It is a file"
      p = subprocess.Popen(['sha1sum',inDir+"/"+nub], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      out, err = p.communicate()
      inFileSHA = out.split()
      p = subprocess.Popen(['sha1sum',basePath+"/"+user+"/"+tierPath+"/"+nub], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      out, err = p.communicate()
      outFileSHA = out.split()
      if verbose:
        print "    The input SHA1:", inFileSHA[0], "vs the output SHA1:", outFileSHA[0]
      if inFileSHA[0] == outFileSHA[0]:
        if verbose:
          print "    The file was correctly copied, we can delete the input file"
        command = "rm "+inDir+"/"+nub
        if dryRun:
          print command
        else:
          p = subprocess.Popen(['rm',inDir+"/"+nub], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          out, err = p.communicate()
      else:
        if verbose:
          print "    The file was not correctly copied, delete the copied file"
        correctlyCopied = False
        tier = "srm://srm01.ncg.ingrid.pt:8444/srm/managerv2?SFN=/cmst3/store/user/"
        cmd = 'clientSRM Rm -e httpg://srm01.ncg.ingrid.pt:8444 -s "' + tier+user+"/"+tierPath+"/"+nub + '" >> LOG &'
        if dryRun:
          print command
        else:
          p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          out, err = p.communicate()
    if os.path.isdir(inDir+"/"+nub):
      if verbose:
        print "  It is a directory"
      if os.path.isdir(basePath+"/"+user+"/"+tierPath+"/"+nub):
        if verbose:
          print "  The directory exists in the output too, so we can proceed to recursively check it"
        if recursiveConsolidate(inDir+"/"+nub, tierPath+"/"+nub, user, basePath, dryRun):
          command = "rm -r "+inDir+"/"+nub
          if dryRun:
            print command
          else:
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
        else:
          correctlyCopied = False
      else:
        if verbose:
          print "The directory does not exist in the output, so we do not recurse"
        correctlyCopied = False

  return correctlyCopied

if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description='Process the command line options')
  parser.add_argument('-d', '--dryRun', action='store_true', help='Do a dry run (i.e. do not actually run the commands to remove the corrupt files from the output and the correctly copied files from the input)')
  parser.add_argument(      '--verbose', action='store_true', help='Have verbose output')
  parser.add_argument('-u', '--user', required=True, help='Username to be used to check if the files were correctly copied')
  parser.add_argument('-i', '--inDir', required=True, help='Input path, the full path from where the files were copied')
  parser.add_argument('-o', '--outDir', required=True, help='Output path, the path where the files were supposed to be copied to (will be used with the username to build the full output path)')
  parser.add_argument(      '--basePath', default='/gstore/t3cms/store/user', help='The base path with which to access the files on the tier storage')

  args = parser.parse_args()
  verbose = args.verbose

  print "This script will check whether the files from the input directory were successfully copied to the output path on the tier storage."
  print "  The chosen input directory:", args.inDir
  print "  The chosen output path:", args.outDir
  print "  The defined user:", args.user
  print "  The full path to the tier storage:", args.basePath+"/"+args.user+"/"+args.outDir

  if not args.dryRun:
    print "You did not enable dry run. You are on your own!"

  print "############### Make sure you run the voms-proxy-init command with the correct arguments and that you have a valid proxy throughout the execution"

  if recursiveConsolidate(args.inDir, args.outDir, args.user, args.basePath, args.dryRun):
    print "All files have been correctly copied!!!!!!!!!!!"
