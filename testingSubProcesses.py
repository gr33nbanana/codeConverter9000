import subprocess as sp
from glob import glob
import os
import pathlib

def filterForType(location = str( input("Enter full path to look in:\n") ),
fileType = str( input("Enter filetype to look for:\n") ),
subFolders = input("Should subfolders be included?") ):
  output = sp.getoutput('dir -1 %s %s' %(location, subFolders))
  globArgument = '*.%s'%fileType
  doRecursive = False

  if (len(subFolders) >= 1 and subFolders.lower()[0] == "y"):
      globArgument = '**/' + globArgument
      doRecursive = True

  outputlines = glob(globArgument, recursive = doRecursive)

  for fileName in outputlines:
    #print("FILE NAME: ", fileName)

    #checks if the last characters are the same as fileType
    #if fileName[-len(fileType) : ] == fileType:
        #filename contains 'fullpath/filename'
    outPutName = fileName[: - len(fileType)]
    outPutName = outPutName.__add__('f90')
    findentArg = "findent -ofree < {0} > {1} ".format(fileName, outPutName)
    removeArg = 'rm ' + fileName

    try:
        print(findentArg)
        sp.call(findentArg, shell = True)
    except:
        print("Error while trying to run findent")
    try:
        print("Removing " + fileName)
        os.remove(fileName)
    except:
        print("Error while deleting file: " + fileName)



#since the code can only compile in Ubuntu, run make clean, make built and dump .o files

def runMakeCleanBuilt():
    try:
        print("Running make cleand and make built")
        sp.call("make clean", shell = True)
        sp.call("make built", shell = True)
    except:
        print("Are you sure make file is in this directory?")

def gatherOldDumpedOFiles():
    sp.call("mkdir -p ./DumpedFiles", shell = True)
    for fileRef in pathlib.Path('.').glob('**/*.o'):
        fileName = str(fileRef)
        # fileName[fileName.rfind('/') + 1 : ] gives the string after the last occurance of '/' which is the name of the .o file so that it prints in the DumpedFiles directory
        print("objdump -d " + fileName + " > " + "/DumpedFiles/" + fileName[fileName.rfind('/') + 1 : ] + ".f.asm")

        sp.call("objdump -d " + fileName + " > " + "/DumpedFiles/" + fileName[fileName.rfind('/') + 1 : ] + ".f.asm", shell = True)
        sp.call("strings -d " + fileName + " > " + "/DumpedFiles/" + fileName[fileName.rfind('/') + 1 : ] + ".f.txt", shell = True)

def gatherNewDumpedOFiles():
    sp.call("mkdir -p ./DumpedFiles", shell = True)
    for fileRef in pathlib.Path('.').glob('**/*.o'):
        fileName = str(fileRef)
        print("objdump -d " + fileName + " > " + "/DumpedFiles/" + fileName[fileName.rfind('/') + 1 : ] + ".f90.asm")

        sp.call("objdump -d " + fileName + " > " + "/DumpedFiles/" + fileName[fileName.rfind('/') + 1 : ] + ".f90.asm", shell = True)
        sp.call("strings -d " + fileName + " > " + "/DumpedFiles/" + fileName[fileName.rfind('/') + 1 : ] + ".f90.txt", shell = True)

def checkForDifference():
    #sp.call("mkdir -p ./Diff", shell = True)

    for fileRefOne, fileRefTwo in zip( pathlib.Path('.').glob("*.f.asm"), pathlib.Path('.').glob("*.f90.asm") ):
        fileOne = str(fileRefOne)
        fileTwo = str(fileRefTwo)
        fileOneName = fileOne[ fileOne.rfind('/') + 1 : ]
        fileTwoName = fileTwo[ fileTwo.rfind('/') + 1 : ]
        outputFileName = ("difference_" + fileOneName + "__" + fileTwoName).replace('.', '')
        outputFileName = outputFileName + ".txt"
        shellArgument = "diff -B -Z " + fileOne + " " + fileTwo + " > ./Diff/" + outputFileName

        print(shellArgument)
        #sp.call("diff -B -Z " + fileOne + " " + fileTwo + " > ./Diff/ " + outputFileName, shell = True)
        sp.call(shellArgument, shell = True)


#runMakeCleanBuilt()
#gatherOldDumpedOFiles()

#filterForType()

#runMakeCleanBuilt()
#gatherNewDumpedOFiles()

checkForDifference()

#sp.call("diff -B -Z a3dapip.o.f.asm a3dapip.o.f90.asm > ./Diff/Python_Diff__erence.txt", shell = True)
