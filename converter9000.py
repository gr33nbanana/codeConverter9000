"""Converter9000.py

Usage:
  converter9000.py convert (<fromtype> <totype>) [--path=<location> --dump_at=<dumppath> --identifier=<extension> --withMake] [--only=<filename>... | --recursive]
  converter9000.py sisyphus <fromtype> (uphill | downhill) [--path=<location> --dump_at=<dumppath> --clean --fromMake --Hera][--withMake | --withCMake] [--only=<filename>... | --recursive]
  converter9000.py hephaestus (--withMake | --withCMake) [--identifier=<extension> --dump_at=<dumppath> --only=<filename>... --fromMake --onlyAssembly --onlyStrings]

Commands:
  convert            The program saves the converted files with a different name and checks for differences between the old and new files in the assembly code and string data

                     Sisyphus does either half of the work
  sisyphus           Uphill only runs findent and saves the file with the same filename so that the changes are checked within GitKraken or other version control
                     Downhill recompiles the program and overwrites the assembly and string files

  hephaestus         Runs the make file and saves assembly code and strings


Arguments:
  <fromtype>         Filetype to be converter only .f supported now
  <totype>           Filetype to convert to only .F90 supported now
  <dumppath>         Folder path where .o file information is saved
  <diffpath>         Folder path where to gather results from diff
  <filename>         Name of the file to convert including extension.
  <extension>        Optional extension for saved asm file when running hephaestus

Options:
  -h --help                 Show this documentation.

  --identifier=<extension>               Specify if the saved asm should have an indentifiying extension in their name e.g.'file.extension.asm'. [default: ]

  --version                 Show version.

  -p --path=<>              The path of the folder or files to be converted if it is not the current path. Include last forward slash. E.g. './work_folder/this_folder/' [default: ./]
  s
  -r --recursive            If specified the program will run recursively

  -o --only <name1,name2>   Only convert the given files or files seperated by comma.Include file extension.\n\t\t\t    -o file1.txt,file2.cpp,file3.f...

  --dump_at=<>              Specify a different folder (created if not existant) to gather .o file information [default: ./DumpedFiles/]

  --clean                   Removes all temporary _.F90 files and the corresponding formated .f files and saves a single .F90 file [default: False]

  --fromMake                Specifies if program is called from a Makefile. Files specified with --only are understood to be object files [default: False]

  --withMake                Specify if you want to also run a make command to build the project, compiling any changed file. Should be careful if running it with sisyphus downhill as if helper '_.F90' files are not deleted they will compile and create redundant object files. [default: False]

  --withCMake              Specify if the files are built using CMake instead of make. compiling any changed file. Should be careful if running it with sisyphus downhill as if helper '_.F90' files are not deleted they will compile and create redundant object files. [default: False]

  --Hera                    Rejects hephaestus for being ugly, hephaestus() does not run 'make built' or gather .asm files [default: False]

  --onlyAssembly            Specifies that only the .asm data should be saved from object files [default: False]

  --onlyStrings             Specifies that only the .txt string data should be saved from object files [default: False]

"""

from docopt import docopt
import subprocess as sp
from glob import glob
import os
import pathlib
import shutil
import multiprocessing as mp
from functools import partial
import time
import fnmatch
import warnings

args = docopt(__doc__, version = '3.0')
#location = './' by default, something like 'D:/Uni/' if specified
def compileFiles():
    """Calls the make or CMake command line for compiling the project.
    """
    if(args['--withMake']):
        sp.call("make built", shell = True)
    elif(args['--withCMake']):
        sp.call("cd _build && make", shell= True)
def collectPaths(location = args['--path'], fromType = args['<fromtype>']):
    """Returns a list of all files in the specified --path with the specified extension <fromtype>
    """
    globArgument = location + f"*{fromType}"        #'*%s'%fromType
    if ( args['--recursive'] == True ):
        globArgument = location + f"**/*{fromType}"#'**/*%s'%fromType
    if(len(args['--only']) > 0):
        #args['--only'][0] is the string "file1.txt,file2.cpp..."
        #parses the string to a list of file names
        files = args['--only'][0].split(',')
        paths = [location + name for name in files]
        #paths = ["./location/fileone.f", "./location/filetwo.f", ["./location/" + "filename.f"]
        #print("DEBUGGING: COLLECTED PATHS:\n" + str(paths))
    elif(len(args['--only']) == 0):
        #paths = glob("full/path/filename(.f)<-dot in fromType string")
        paths = glob(globArgument, recursive = args['--recursive'])
    try:
        #Read the gitignore file to remove all paths and files which git ignores.
        with open(".gitignore",'r') as file:
            print("Reading gitignore file")
            ignoreInfo = file.readlines()
            for line in ignoreInfo:
                if(line[0] == '#'):
                    ignoreInfo.remove(line)
        for idx, line in enumerate(ignoreInfo):
            ignoreInfo[idx] = line.replace("\n", "*")
            ignoreInfo[idx] = './' + ignoreInfo[idx]
            #paths need './' for root, and * at end to ignore anything starting with the specified characters
            # './_*' -- for ./_build etc
            # './*.o*' for any ./path/file.F90.o* file
        print(f"IgnoreInfo: {ignoreInfo}")
        #paths have been collected
        #Remove all matching gitignore paths from the return path list
        paths = [n for n in paths if not any(fnmatch.fnmatch(n,ignore) for ignore in ignoreInfo)]


    except:
        warnings.warn("Warning: No .gitignore file found, cannot exclude paths not under version control in current folder")
        if(input("Do you wish to continue? y/n: ").upper() == 'Y'):
            pass
        else:
            raise SystemExit
    return paths

def filterForType( location = args['--path'], fromType = args['<fromtype>'], toType = args['<totype>'], remove = True, sisyph = args['sisyphus'] ):
    """Runs findent on collected paths from collectPaths(),
    if sisyphus -- overwrites .f files with free format
    if remove   -- removes all paths from collectPaths(), intended for removing helper files '_.F90'
    """
    #location = './' by default, something like 'D:/Uni/' if specified
    #<fromtype> = '.f' '.F90' contains a dot
    #<totype>   = '.f' '.F90' contains a dot
    outputlines = collectPaths()

    for basePathAndName in outputlines:
        #basePathAndName contains   'fullpath/filename.f'            | fullpath/filename{fromType}
        #outputPathAndName contains 'fullopath/filename_.F90 or .F90 | fullpath/filename{toType}
        outputPathAndName = basePathAndName[: - len(fromType)]
        outputPathAndName = outputPathAndName.__add__(toType)
        #Extra formatting for Windows
        outputPathAndName = str(outputPathAndName).replace("\\","/")
        basePathAndName = str(basePathAndName).replace("\\","/")

        findentArg = "findent -ofree < {oldFile} > {newFile} ".format(oldFile = basePathAndName, newFile = outputPathAndName)
        try:
            print(findentArg)
            sp.call(findentArg, shell = True)
        except:
            print("Error while trying to run findent\nFiles might not be in the current or specified path")
        if(sisyph):
            #Overwrite the fixed format code in basePathAndName with the free format code in outputPathAndName
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
#TODO :: Convert paths to absolute pahts after getting them in docopt
def runMakeCleanBuilt():
    """
    Runs the functions to compile the program if the optional flgas are given
    """
    try:
        #If --withMake or --withCMake is specified do not call 'make built'
        if (args['--withMake'] or args['--withCMake']):
            print("Compiling program")
            #sp.call("make", shell = True)
            compileFiles()
    except:
        print("No option given for compilation. Add --withMake or --withCMake when calling the script.")
#For now only works for gatherDumpedOFiles and outputfolder is defined, can be generalized to have any outputfolder (from different functions) But would need to change pool.map!(check doc)
def runOnFiles(givenName, outputFolder = args['--dump_at'], fileType = ""):
    """
    givenName:    str (pathName of object file)
    outputFolder: str, path where to save the assembly files
    fileType:     str, add an additional extension to the filename, controlled by --extension option
    Runs parallel on individual path name of object files, gathering the assembly code and string data.
    """
    #Runs 'objdump -d filename.o > filename.asm' on all given object files to save assembly code
    #Returns a list of the commands it ran, return object is later printed
    fileName = givenName
    #Given name is a single file PATH when the function is called from multirpocesses Pool function
    returnArg1 = ''
    returnArg2 = ''
    #############################################################
    #Following two ifs statements control saving BOTH strings and assembly if nothing is specified, and only strings or only assembly information if one of them is specified.
    if(not args['--onlyStrings'] or args['--onlyAssembly']):
        #########
        #Runs by default, if --onlyStrings is specified, doesnt' run, if --onlyAssembly is specified only this shellarg runs, no string data saved
        #########
        #objdump -d someFolder/name.o > outputFolder/name.fileType.asm
        #argument = "objdump -d " + fileName + " > " + outputFolder + os.path.basename(fileName) + "." + fileType + ".asm"
        shellArgument = "objdump -d {objectName} > {outputPath}{name}{extension}.asm"
        shellArgument = shellArgument.format(objectName = fileName, outputPath = outputFolder, name = os.path.basename(fileName), extension = fileType)
        #print(shellArgument)
        #printList.append(shellArgument)\
        #
        sp.call(shellArgument, shell = True)
        returnArg1 = shellArgument

    if(not args['--onlyAssembly'] or args['--onlyStrings']):
        ########
        #Runs by default, if --onlyAssembly is specified it doesnt' run, if --onlyStrings is specified only this shellarg runs, no asm data saved
        ########
        #printList.append(shellArgument)
        #shellArgument = "strings -d " + fileName + " > " + outputFolder + os.path.basename(fileName) + "." + fileType + ".txt"
        shellArgument = "strings -d {objectName} > {outputPath}{name}{extension}.txt"
        shellArgument = shellArgument.format(objectName = fileName, outputPath = outputFolder, name = os.path.basename(fileName), extension = fileType )

        sp.call(shellArgument, shell = True)
        returnArg2 = shellArgument
    #############################################################
    #print(shellArgument)
    returnShellArgument = "{shellArgument1}, {shellArgument2}".format(shellArgument1 = returnArg1, shellArgument2 = returnArg2)
    return returnShellArgument

calledCommands = []
#mostly a filler function to pass to map_async and get all the shell arguments that are returned
def testCallBack(resultObject):
    """resultObject: result given back by the parallel function.
    appends resultObject to a global caledCommands list, to print after all function calls have been made
    """
    global calledCommands
    calledCommands.append(resultObject)
    print("DONE")

def gatherDumpedOFiles( extension = args["--identifier"], outputFolder = args['--dump_at'] ):
    """
    extension:    string
    outputFolder: string
    Gathers the assembly and string data from object files. If extension is specified, inserts the given string in the name of the output assembly file: 'fileName.extension.asm'
    """
    startTime = time.time()
    #extension is only information about the source of the object files and just gets added to the saved file name
    if(args['sisyphus']):
        extension = ''
    if not ( pathlib.Path(args['--dump_at']).exists() ):
        #If there is no folder specified for dumping the assembly code, make one.
        os.mkdir(outputFolder)
    #Run in parallel the following:
    #objdump -d ./folders/file.o > file.o.asm
    #collects .o files recursively
    #Collect print statements in global list to not run print() all the time
    print("Gathering Assembly code and Strings")
    pathList = []
    #Makefile provides object file names seperated by space
    # whereas docopt seperates by comma
    # Handle which files toa add to pathlist:
    if( len(args['--only']) > 0 and args['--fromMake']):
        changedOFiles = args['--only'][0].split(' ')
        print(" FILES ASSIGNED TO pathList: ", changedOFiles)
        pathList = changedOFiles
    elif( len(args['--only']) > 0 and not args['--fromMake'] ):
        onlyFiles = args['--only'][0].split(',')
        for fileName in onlyFiles:
            oName = pathlib.Path(fileName).with_suffix('.o')
            for oPathAndName in pathlib.Path('.').glob(f"**/{oName}"):
                pathList.append(oPathAndName)
        #paths = [args['--path'] + name for name in oFiles]
        #pathList = paths
    else:
        #pathList has to be made here so that it contains strings and not PosixPaths
        for filePath in pathlib.Path('.').glob('**/*.o'):
            #strPath = str(filePath)
            pathList.append(strPath)
    #Function can be passed to mulitple threads for parralel processing
    #chunkSize can be specified, not much performance increase
    #chunkSize = int(len(pathList) / mp.cpu_count() )
    pool = mp.Pool(mp.cpu_count(), maxtasksperchild = 2)
    func = partial(runOnFiles, fileType = extension )
    #try:
    #print(f"Gathering ASM from : {pathList}")
    pool.map_async(func, pathList, callback = testCallBack)
    ##
    #finally:
    pool.close()
    pool.join()
    ##
    print(calledCommands)
    print(len(calledCommands))
    #runOnFiles(pathList)
    endTime = time.time()
    #print(printList)
    print("Runtime: {duration} seconds".format(duration = (endTime - startTime)) )

def checkForDifference( givenType ):
    """OUTDATED! UNUSED!
    Checks if there are differences in /DumpedFiles for the givenType ('asm' or 'txt') between the <fromtype> and <totype> passed to the script.
    """
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
    newFileType = args['<totype>']   #example .F90
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
    if not (args['--Hera']):
        runMakeCleanBuilt()
        gatherDumpedOFiles()
    else:
        print("Hephaestus did not run. Rejected by Hera for being ugly.")

def renameAndClean():
    """Runs collectPaths() for '_.F90' helper files and renames the corresponding '.f' files to have the proper '.F90' extension.
    If '--clean' option is given it will delete the '_.F90' helper files
    Only renames 30 files then prompts a user key stroke. Pausing is inteded to check if GitKraken or other Version Control has correctly detected a rename."""
    paths = collectPaths(fromType = '_.F90')
    maxCount = 30
    for pathName in paths:
        if(maxCount <= 0):
            maxCount = 30
            #GitKraken cannot process more than 60-120 files at a time, before the changes stop being recognized as rename and become delte + create, loosing the commit history
            input("Renaming paused. Check if Version control can handle the amount of renamed files.\nPress any key to continue")
        maxCount -= 1
        #print("PATHS: " + str(paths))
        #pathName   = path/filename_.F90
        #outputPath = path/filename.F90
        #oldPath    = path/filename.f
        outputPath = pathName[:-len("_.F90")] + ".F90"
        oldPath = pathName[:-len("_.F90")] + ".f"
        #Extra formatting for windows
        pathName = pathName.replace("\\","/")
        outputPath = outputPath.replace("\\","/")
        oldPath = oldPath.replace("\\","/")
        if(args['--clean']):
            os.remove(pathName)
        try:
            shellArg = f"git mv {oldPath} {outputPath}"
            sp.call(shellArg, shell=True)
            print(shellArg)
        except:
            print(f"Could not execute {shellArg}")
            continue

if __name__ == '__main__':
    if(args['convert']):
        if not ( pathlib.Path(args['--dump_at']).exists() ):
            print("No dumped assembly directory detected.\nWill compile program and save assembly code")
            hephaestus()
        #Only convert files and save them with the same name
        filterForType(toType = '_.F90', remove = False)
        renameAndClean()
        hephaestus()



    elif(args['sisyphus'] and args['uphill']):
        #Save assembly code if it wasn't done
        if not ( pathlib.Path(args['--dump_at']).exists() ):
            print("No dumped assembly directory detected.\nWill compile program and save assembly code")
            hephaestus()

        #Only convert files and save them with the same name
        filterForType(toType = '_.F90', remove = False)

    elif(args['sisyphus'] and args['downhill']):
        if not ( pathlib.Path(args['--dump_at']).exists() ):
            print("WARNING: No dumped assembly directory detected. Make sure it exists in the given --dump_at location.\nIf you wish to compile for the first time use the hephaestus command.\nOtherwise use sisyphus uphill to format files first.")
            raise SystemExit
        #The files should be converted but kept with the same name
        #Program recompiles with new object files (assumeing old files were changed first)
        #Overwrites object files assembly and string code
        #
        renameAndClean()
        hephaestus()


    elif(args['hephaestus']):
        hephaestus()
