"""Converter9000.py

Usage:
  converter9000.py convert <fromtype> <totype>[--path=<location>] [--only=<filename>... | --recursive]

Arguments:
  <fromtype>         filetype to be converter only .f supported now
  <totype>           filetype to convert to
Options:
  -h --help          Show this documentation.
  --version          Show version.
  -p --path=<>       The path of the folder or files to be converted if it is not the current path [default: ./]
  -r --recursive     If specified the program will run recursively
  -o --only <name>   Only convert the give files

"""

from docopt import docopt
import subprocess as sp
from glob import glob
import os
import pathlib

args = docopt(__doc__, version = '0.1')


def filterForType( location = args['--path'], fromType = args['<fromtype>'], toType = args['<totype>'] ):
    #location = './' by default, something like 'D:/Uni/' if specified
    #fileType = '.f' '.f90'
    globArgument = location + '*%s'%fromType

    if ( args['--recursive'] == True ):
      globArgument = location + '**/*%s'%fromType

    outputlines = glob(globArgument, recursive = args['--recursive'])

    for fileName in outputlines:
        #checks if the last characters are the same as fileType
        #if fileName[-len(fileType) : ] == fileType:
        #filename contains 'fullpath/filename'
        outPutName = fileName[: - len(fromType)]
        outPutName = outPutName.__add__(toType)
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

        shellArgument = "strings -d " + fileName + " > " + outputFolder + fileName[fileName.rfind('/') + 1 : ] + "." + fileType + ".txt"
        print(shellArgument)
        sp.call(shellArgument, shell = True)

def checkForDifference( thisType ):
    sp.call("mkdir -p ./Diff", shell = True)
    print("CHECKING DIFFERENCES")
    #File location
    fileLocation = './DumpedFiles/'
    outputFolder = './Diff/'

    for fileRefOne, fileRefTwo in zip( pathlib.Path( fileLocation ).glob("*.f." + thisType ), pathlib.Path(fileLocation).glob("*.f90." + thisType) ):
        fileOne = "./" + str(fileRefOne)
        fileTwo = "./" + str(fileRefTwo)
        #fileOne ./DumpedFiles/someName.f.asm or ./DumpedFiles/someName.f.txt

        fileOneName = fileOne[ fileOne.rfind('/') + 1 : ]
        fileTwoName = fileTwo[ fileTwo.rfind('/') + 1 : ]
        #fileOnename = someName.f.asm or someName.f.txt

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
            print(shellArgument + saveShellArgument)
            sp.call(shellArgument + saveShellArgument ,shell = True)


#Make gathering O files have arguments for the format so that the same function is called before and after formatting but with different format arguments


runMakeCleanBuilt()
gatherDumpedOFiles('f')

filterForType()

runMakeCleanBuilt()
gatherDumpedOFiles('f90')

checkForDifference('asm')
checkForDifference('txt')
