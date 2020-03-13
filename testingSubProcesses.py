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


def gatherDumpedOFiles( fileType ):
    #objdump -d ./folders/file.o > file.o.asm
    sp.call("mkdir -p ./DumpedFiles", shell = True)
    #collects .o files recursively
    outputFolder = "./DumpedFiles/"
    for fileRef in pathlib.Path('.').glob('**/*.o'):
        fileName = str(fileRef)
        shellArgument = "objdump -d " + fileName + " > " + outputFolder + fileName[fileName.rfind('/') + 1 : ] + "." + fileType + ".asm"
        print(shellArgument)

        sp.call(shellArgument, shell = True)
        sp.call("strings -d " + fileName + " > " + outputFolder + fileName[fileName.rfind('/') + 1 : ] + "." + fileType + ".txt", shell = True)

def checkForDifference( thisType ):
    sp.call("mkdir -p ./Diff", shell = True)
    print("CHECKING DIFFERENCES")
    #File location
    fileLocation = './DumpedFiles/'
    outputFolder = './Diff/'

    for fileRefOne, fileRefTwo in zip( pathlib.Path( fileLocation ).glob("*.f." + thisType ), pathlib.Path(fileLocation).glob("*.f90." + thisType) ):
        fileOne = "./" + str(fileRefOne)
        fileTwo = "./" + str(fileRefTwo)

        fileOneName = fileOne[ fileOne.rfind('/') + 1 : ]
        fileTwoName = fileTwo[ fileTwo.rfind('/') + 1 : ]

        outputFileName = ("difference_" + thisType + "__" + fileOneName + "__" + fileTwoName).replace('.', '')
        outputFileName = outputFileName + ".txt"

        shellArgument = "diff -B -Z " + fileOne + " " + fileTwo
        saveShellArgument = " > " + outputFolder + outputFileName

        print(shellArgument)
        #save the output of diff to see if its empty or not
        #sp.call apperently returns an integer which is 0 if the difference is empty
        difference = sp.call(shellArgument, shell = True)

        if difference != 0:
            print("DIFFERENCE IN " + fileOneName + " AND " + fileTwoName)
            sp.call(shellArgument + saveShellArgument ,shell = True)


#Make gathering O files have arguments for the format so that the same function is called before and after formatting but with different format arguments


#runMakeCleanBuilt()
#gatherDumpedOFiles('f')

#filterForType()

#runMakeCleanBuilt()
#gatherDumpedOFiles('f90')

checkForDifference('asm')
checkForDifference('txt')
