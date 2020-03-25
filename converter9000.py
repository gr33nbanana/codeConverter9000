"""Converter9000.py

Usage:
  converter9000.py convert (<fromtype> <totype>) [--path=<location> --dump_at=<dumppath> --diff_at=<diffpath>] [--only=<filename>... | --recursive]
  converter9000.py sisyphus <fromtype> (uphill | downhill) [--path=<location> --dump_at=<dumppath>] [--only=<filename>... | --recursive]


Commands:
  convert            The program saves the converted files with a different name and checks for differences between the old and new files in the assembly code and string data

                     Sisyphus does either half of the work
  sisyphus           Uphill only runs findent and saves the file with the same filename so that the changes are checked within GitKraken or other version control
                     Downhill recompiles the program and overwrites the assembly and string files


Arguments:
  <fromtype>         Filetype to be converter only .f supported now
  <totype>           Filetype to convert to
  <dumppath>         Folder path where .o file information is saved
  <diffpath>         Folder path where to gather results from diff

Options:
  -h --help          Show this documentation.
  --version          Show version.
  -p --path=<>       The path of the folder or files to be converted if it is not the current path [default: ./]
  -r --recursive     If specified the program will run recursively
  -o --only <name>   Only convert the given files
  --dump_at=<>       Specify a different folder (created if not existant) to gather .o file information [default: ./DumpedFiles/]
  --diff_at=<>       Specify a folder in which to save the output files from checkForDifference [default: ./Diff/]

"""

from docopt import docopt
import subprocess as sp
from glob import glob
import os
import pathlib

args = docopt(__doc__, version = '0.2')


def filterForType( location = args['--path'], fromType = args['<fromtype>'], toType = args['<totype>'], remove = True ):
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

        if(remove):
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


def gatherDumpedOFiles( fileType, outputFolder = args['--dump_at'] ):
    try:
        os.mkdir(outputFolder)
    except:
        pass
    #objdump -d ./folders/file.o > file.o.asm
    #collects .o files recursively
    for fileRef in pathlib.Path('.').glob('**/*.o'):
        fileName = str(fileRef)
        #objdump -d someFolder/name.o > outputFolder/name.fileType.asm
        shellArgument = "objdump -d " + fileName + " > " + outputFolder + os.path.basename(fileName) + "." + fileType + ".asm"
        print(shellArgument)
        sp.call(shellArgument, shell = True)

        shellArgument = "strings -d " + fileName + " > " + outputFolder + os.path.basename(fileName) + "." + fileType + ".txt"
        print(shellArgument)
        sp.call(shellArgument, shell = True)

def checkForDifference( givenType ):
    #Checks for difference in the asembly and string output of a set of object files
    #Object files before running findent contain <fromType> in their name
    #Object files after running findent contain <toType> in their name

    #default "mkdir ./Diff/"
    try:
        os.mkdir(args['--diff_at'])
    except:
        pass
    print("CHECKING DIFFERENCES")
    #File location
    fileLocation = args['--dump_at'] #default ./DumpedFiles/
    outputFolder = args['--diff_at'] #default: ./Diff/
    oldFileType = args['<fromtype>'] #example .f
    newFileType = args['<totype>']   #example .f90
    diffOptions = " -B -Z --strip-trailing-cr "

    for fileRefOne, fileRefTwo in zip( pathlib.Path( fileLocation ).glob("*"+ oldFileType + givenType ), pathlib.Path(fileLocation).glob("*" + newFileType + givenType) ):
        fileOne = "./" + str(fileRefOne)
        fileTwo = "./" + str(fileRefTwo)
        #fileOne ./DumpedFiles/someName.f.asm or ./DumpedFiles/someName.f.txt

        fileOneName = os.path.basename(fileOne) #fileOne[ fileOne.rfind('/') + 1 : ]
        fileTwoName = os.path.basename(fileTwo) #fileTwo[ fileTwo.rfind('/') + 1 : ]
        #fileOnename = someName.f.asm or someName.f.txt

        outputFileName = ("difference_" + givenType + "__" + fileOneName + "__" + fileTwoName).replace('.', '-')
        outputFileName = outputFileName + ".txt"

        shellArgument = "diff" + diffOptions + fileOne + " " + fileTwo
        saveShellArgument = " > " + outputFolder + outputFileName

        print(shellArgument)
        #save the output of diff to see if its empty or not
        #sp.call apperently returns an integer which is 0 if the difference is empty
        difference = sp.call(shellArgument, shell = True)

        if difference != 0:
            print("DIFFERENCE IN " + fileOneName + " AND " + fileTwoName)
            print(shellArgument + saveShellArgument)
            sp.call(shellArgument + saveShellArgument ,shell = True)

def hephaestus():
    runMakeCleanBuilt()
    gatherDumpedOFiles(fileType = args['<fromtype>'])

if __name__ == '__main__':
    if(args['convert']):
        #Create Object files from old format types
        runMakeCleanBuilt()
        #Gather the assembly code and string information
        gatherDumpedOFiles( fileType = args['<fromtype>'] )
        filterForType()
        #Re compile the program for new object files
        runMakeCleanBuilt()
        #Gather new assembly code and strings
        gatherDumpedOFiles( fileType = args['<totype>'] )
        #run diff between the old and new assembly files
        checkForDifference('.asm')
        checkForDifference('.txt')

    elif(args['sisyphus'] and args['uphill']):
        #Save assembly code if it wasn't done
        if not ( pathlib.Path(args['--dump_at']).exists() ):
            print("No dumped assembly files detected.\nWill compile program and save assembly code")
            hephaestus()

        #Only convert files and save them with the same name
        filterForType(toType = args['<fromtype>'], remove = False)

    elif(args['sisyphus'] and args['downhill']):
        #The files should be converted but kept with the same name
        #Program recompiles with (presumebly) new object files
        #Overwrites object files assembly and string code
        hephaestus()
