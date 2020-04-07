"""Converter9000.py

Usage:
  converter9000.py convert (<fromtype> <totype>) [--path=<location> --dump_at=<dumppath> --diff_at=<diffpath>] [--only=<filename>... | --recursive]
  converter9000.py sisyphus <fromtype> (uphill | downhill) [--path=<location> --dump_at=<dumppath> --clean] [--only=<filename>... | --recursive]
  converter9000.py hephaestus <fromtype> [--dump_at=<dumppath>]

Commands:
  convert            The program saves the converted files with a different name and checks for differences between the old and new files in the assembly code and string data

                     Sisyphus does either half of the work
  sisyphus           Uphill only runs findent and saves the file with the same filename so that the changes are checked within GitKraken or other version control
                     Downhill recompiles the program and overwrites the assembly and string files

  hephaestus         Runs the make file and saves assembly code and strings


Arguments:
  <fromtype>         Filetype to be converter only .f supported now
  <totype>           Filetype to convert to only .f90 supported now
  <dumppath>         Folder path where .o file information is saved
  <diffpath>         Folder path where to gather results from diff

Options:
  -h --help                 Show this documentation.
  --version                 Show version.
  -p --path=<>              The path of the folder or files to be converted if it is not the current path [default: ./]
  -r --recursive            If specified the program will run recursively
  -o --only <name1,name2>   Only convert the given files or files seperated by comma -o file1.txt,file2.cpp...
  --dump_at=<>              Specify a different folder (created if not existant) to gather .o file information [default: ./DumpedFiles/]
  --diff_at=<>              Specify a folder in which to save the output files from checkForDifference [default: ./Diff/]
  --clean                   Removes all temporary _.f90 files and the corresponding formated .f files and saves a single .f90 file [default: False]

"""

from docopt import docopt
import subprocess as sp
from glob import glob
import os
import pathlib
import shutil

args = docopt(__doc__, version = '0.2')
#location = './' by default, something like 'D:/Uni/' if specified

def collectPaths(location = args['--path'], fromType = args['<fromtype>']):
    globArgument = location + '*%s'%fromType
    if ( args['--recursive'] == True ):
        globArgument = location + '**/*%s'%fromType

    if(len(args['--only']) > 0):
        #args['--only'][0] is the string "file1.txt,file2.cpp..."
        #parses the string to a list of file names
        files = args['--only'][0].split(',')
        #["./location/fileone.f", "./location/filetwo.f", ["./location/" + "filename.f"]
        paths = [location + name for name in files]
        #print("PATHS:\n" + str(paths))
    elif(len(args['--only']) == 0):
        #paths = glob("full/path/filename(.f)<-dot in fromType string")
        paths = glob(globArgument, recursive = args['--recursive'])
    return paths

def filterForType( location = args['--path'], fromType = args['<fromtype>'], toType = args['<totype>'], remove = True, sisyph = args['sisyphus'] ):
    #location = './' by default, something like 'D:/Uni/' if specified
    #<fromtype> = '.f' '.f90' contains a dot
    #<totype>   = '.f' '.f90' contains a dot
    outputlines = collectPaths()

    for basePathAndName in outputlines:
        #basePathAndName contains   'fullpath/filename.f'            | fullpath/filename{fromType}
        #outPutPathAndName contains 'fullopath/filename_.f90 or .f90 | fullpath/filename{toType}
        outputPathAndName = basePathAndName[: - len(fromType)]
        outputPathAndName = outputPathAndName.__add__(toType)
        findentArg = "findent -ofree < {oldFile} > {newFile} ".format(oldFile = basePathAndName, newFile = outputPathAndName)

        try:
            print(findentArg)
            sp.call(findentArg, shell = True)
        except:
            print("Error while trying to run findent\nFiles might not be in the current or specified path")
        if(sisyph):
            catArgument = "cat {copying} > {pasting}".format(copying = outputPathAndName, pasting = basePathAndName)
            print(catArgument)
            shutil.copy2(outputPathAndName, basePathAndName)
            #sp.call(catArgument, shell = True)
            #os.remove(outputPathAndName)

        if(remove):
            try:
                print("Removing " + basePathAndName)
                os.remove(basePathAndName)
            except:
                print("Error while deleting file: " + basePathAndName)

#since the code can only compile in Ubuntu, run make clean, make built and dump .o files

def runMakeCleanBuilt():
    try:
        print("Running make cleand and make built")
        sp.call("make clean", shell = True)
        sp.call("make built", shell = True)
    except:
        print("Are you sure make file is in this directory?")


def gatherDumpedOFiles( fileType, outputFolder = args['--dump_at'] ):
    #fileType is only information about the source of the object files and just gets added to the saved file name
    try:
        os.mkdir(outputFolder)
    except:
        pass
    #objdump -d ./folders/file.o > file.o.asm
    #collects .o files recursively
    for fileRef in pathlib.Path('.').glob('**/*.o'):
        fileName = str(fileRef)
        #objdump -d someFolder/name.o > outputFolder/name.fileType.asm
        #shellArgument = "objdump -d " + fileName + " > " + outputFolder + os.path.basename(fileName) + "." + fileType + ".asm"
        shellArgument = "objdump -d {objectName} > {outputFolder}{name}{extension}.asm"
        shellArgument = shellArgument.format(objectName = fileName, outputFolder = outputFolder, name = os.path.basename(fileName), extension = fileType)
        print(shellArgument)
        sp.call(shellArgument, shell = True)

        #shellArgument = "strings -d " + fileName + " > " + outputFolder + os.path.basename(fileName) + "." + fileType + ".txt"
        shellArgument = "strings -d {objectName} > {outputFolder}{name}{extension}.txt"
        shellArgument = shellArgument.format(objectName = fileName, outputFolder = outputFolder, name = os.path.basename(fileName), extension = fileType )
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
    #givenType                        example .asm
    diffOptions = " -B -Z --strip-trailing-cr "

    for fileRefOne, fileRefTwo in zip( pathlib.Path( fileLocation ).glob("*"+ oldFileType + givenType ), pathlib.Path(fileLocation).glob("*" + newFileType + givenType) ):
        fileOne = "./" + str(fileRefOne)
        fileTwo = "./" + str(fileRefTwo)
        #fileOne ./DumpedFiles/someName.f.asm or ./DumpedFiles/someName.f.txt

        fileOneName = os.path.basename(fileOne) #fileOne[ fileOne.rfind('/') + 1 : ]
        fileTwoName = os.path.basename(fileTwo) #fileTwo[ fileTwo.rfind('/') + 1 : ]
        #fileOnename = someName.f.asm or someName.f.txt

        outputFileName = ("difference_" + givenType + "__" + fileOneName + "_||_" + fileTwoName).replace('.', '-')
        outputFileName = outputFileName + ".txt"

        shellArgument = "diff {options} {firstFile} {secondFile}".format(options = diffOptions, firstFile = fileOne, secondFile = fileTwo)
        saveShellArgument = " > {outputPath}{name}".format(outputPath = outputFolder, name = outputFileName)

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
        filterForType(toType = '_.f90', remove = False)

    elif(args['sisyphus'] and args['downhill']):
        if not ( pathlib.Path(args['--dump_at']).exists() ):
            print("No dumped assembly files detected. Make sure they exist in the given --dump_at location.\nIf you wish to compile for the first time use the hephaestus command.\nOtherwise use sisyphus uphill to format files first.")
            raise SystemExit
        #The files should be converted but kept with the same name
        #Program recompiles with new object files (assumeing old files were changed first)
        #Overwrites object files assembly and string code
        #TODO: rename changed files to .f90
        hephaestus()
        if(args['--clean']):
            paths = collectPaths(fromType = '_.f90')
            for pathName in paths:
                #print("PATHS: " + str(paths))
                #pathName   = path/filename_.f90
                #outputPath = path/filename.f90
                #remPath    = path/filename.f

                outputPath = pathName[:-len("_.f90")] + ".f90"
                remPath = pathName[:-len("_.f90")] + ".f"
                shellArg = "{oldFormatPath} > {newFormatPath}".format(oldFormatPath = pathName, newFormatPath = outputPath)
                print(shellArg)
                os.rename(pathName, outputPath)
                os.remove(remPath)

    elif(args['hephaestus']):
        hephaestus()
