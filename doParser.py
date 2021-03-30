"""DoParser.py

Usage:
  doParser.py declare <extension> (--withMake | --withCMake) [--path=<location> --version_Control_Command=<vc_add>] [--recursive | --only=<filename>...]

Commands:
  declare         Glob for the specified extension files and update DO LOOP for any file which uses the old DO 20 ... 20 last line syntax for DO LOOPS
Arguments:
  <extension>     Extension of files to declare variablse of. Should be '.f' or '.F90'
  <filename>      Name of the file to parse for DO LOOPS including the extension
Options:
  -p --path=<>    The path of the folder or files to change DO LOOPS in. Include last forward slash './path/to/folder/' [default: ./]

  --version_Control_Command=<>  Terminal command to execute in order to stage changes to .asm files when needed [default: git add -A]

  -r --recursive  If specified the program will run recursively

  -o --only <name1,name2>   Only convert the given files or files seperated by comma. Include file extension. For example '-o file1.txt,file2.cpp,file3.f...'

  --withMake                Specify if you want to also run a make command to build the project, compiling any changed file. Should be careful if running it with sisyphus downhill as if helper '_.f90' files are not deleted they will compile and create redundant object files. [default: False]

  --withCMake              Specify if the files are built using CMake instead of make. compiling any changed file. Should be careful if running it with sisyphus downhill as if helper '_.f90' files are not deleted they will compile and create redundant object files. [default: False]
"""
import fnmatch
import warnings
from docopt import docopt
from glob import glob
import re
import subprocess as sp
from pathlib import Path
import time

#TODO :: add docopt documentation
args = docopt(__doc__, version = '1.0')

regex = r"^(?!\!)(.*)?DO[ ]*?(?=\d+)(\d+)[\s\S]*?(?=\n(\s*?\2[\D]+?))"
# ------------------------//-----------------------(\2) \n n-th capturing group, (?:) non storing group
def getMakeCommand():
	"""" Return a string of the relevant terminal command to compile the program, depending on if --withMake or --withCMake was specified"""

	if(args['--withMake']):
		return "make built"
	elif(args['--withCMake']):
		return "cd _build && make"

def compileFiles():
	"""Calls the make or CMake command line for compiling the project.
	"""
	if(args['--withMake']):
		sp.call("make built", shell = True)
	elif(args['--withCMake']):
		sp.call("cd _build && make", shell= True)

def collectPaths(location = args['--path'], fromType = args['<extension>']):
	"""Returns a list of all files in the specified --path with the specified extension <extension>
	"""
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
	try:
		with open(".gitignore",'r') as file:
			print("Reading gitignore file")
			ignoreInfo = file.readlines()
			for line in ignoreInfo:
				if(line[0] == '#'):
					ignoreInfo.remove(line)
		for idx, line in enumerate(ignoreInfo):
			ignoreInfo[idx] = line.replace("\n", "*")
			ignoreInfo[idx] = './' + ignoreInfo[idx]
		print(f"IgnoreInfo: {ignoreInfo}")
		#print(f"paths pre filter: {type(paths)} \n{paths}")

		paths = (n for n in paths if not any(fnmatch.fnmatch(n,ignore) for ignore in ignoreInfo))

		holder = []
		for path in paths:
			holder.append(path)
		#print(f"Holder paths: {holder}")
		paths = holder
		#print(f"returned paths: {paths}")
	except Exception:
		warnings.warn("Warning: No .gitignore file found, cannot exclude paths not under version control in current folder")
		if(input("Do you wish to continue? y/n: ").upper() == 'Y'):
			pass
		else:
			raise SystemExit
	return paths

def compileAndCheck(makeStr):
    """
    Compiles the program using the given makeStr as a command line
    and parses through the terminal output. If it detects '100%' and
    'watchdog' the program has compiled and returns True. Otherwise
    it returns False

    Parameters
    ----------
        makeStr : str
            bash command line to compile the program

    Returns
    -------
        bool
            True of '100%' and 'watchdog' were printed on the terminal
            False otherwise
    """
    print(makeStr)
    # Just return if the process has completed.
    #return sp.Popen().returncode
    proc = sp.Popen(makeStr, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
    procReturnCode = proc.wait()
    if(procReturnCode == 0):
        return True
    else:
        return False
    #flagWATCHDOG = False
    #for line in proc.stdout.readlines():
    #    line = line.decode("utf-8")
    #    print(line)
    #    if('100%' in line and 'watchdog' in line):
    #        flagWATCHDOG = True
    #return flagWATCHDOG

def detectUnstagedDifference(statusCommand, dumpFolderName, desiredExtension):
    """
    Runs the status command and parses through the terminal output. If there are any
    unstaged changes of files in the specified folder with the specified extension
    the function returns True. Otherwise it returns False

    Parameters
    ----------
        statsuCommand : str
            String used to call a subprocess for checking status. The terminal output
            is then parsed for 'Changes not staged for commit' and 'modified'.
        dumpFolderName : str
            Name of the folder of the files for which a modification will be detected.
        desiredExtension : str
            The extension of the files for which a modification will be detected

    Returns
    -------
        bool :
            True if there were detected unstaged modifications in the folder to files
            with the given extension.
            False otherwise.
    """
    proc = sp.Popen(statusCommand, shell = True, stdout = sp.PIPE, stderr=sp.STDOUT)
    flagASM = False
    flagGitNotStaged = False

    for line in proc.stdout.readlines():
        line = line.decode("utf-8")
        print(line)
        if('Changes not staged for commit' in line):
            flagGitNotStaged = True
        if(flagGitNotStaged and 'modified' in line and dumpFolderName in line and desiredExtension in line):
            flagASM = True
    if(flagGitNotStaged and flagASM):
        return True
    else:
        return False

def commitOnlyOneFile(filePath, message = "Bazinga commit"):
    """
    Calls git commands to commit filePath with the given Summary message

    Parameters
    ----------
        filePath : str
            Path of the file to be committed relative to the root git directory
        message : str
            Message which is used for the commit summary
    """
    commitArg = f"git reset && git add {filePath} && git commit -m '{message}'"
    print("\033[1;32;40m " + commitArg + "\033[0;37;40m")
    sp.call(commitArg, shell = True)


def insertInString(originalString, cutIndex1, cutIndex2, stringToInsert):
    """
    Creats a new string with provided string between the indecies of the original string and returns the concatenated string.

    Parameters
    ----------
        originalString : str
            Initial string in which a new one will be 'inserter'
        cutIndex1 : int
            The index (excluding) up to which the originalString is used
            before inserting the desired new string
        cutIndex2 : int
            The index (including) from which the originalString is used
            after adding the desired new string
        stringToInsert : str
            The desired string which will be 'inserted' between cutIndex1 and cutIndex2 of the originalString

    Returns
    -------
        str
            Returns a concatenated string = originalstring[:cutIndex1] + stringToInsert + originalString[cutIndex2:]
     """
    return originalString[:cutIndex1] + stringToInsert + originalString[cutIndex2:]

def insertStrAtIndecies(stringToInsert, originalString, listOfPositions, newLine = False):
    """
    Inserts a string at the give positions in the list of positions. If newLine is set to true the string will be inserted as a newline after the line of the given index

    Parameters
    ----------
        stringToInsert : str
            String which will be added at every index given in the list of indecies
        originalString : str
            String into which a new one will be inserted at all the indecies in the
            list of indecies
        listOfPositions : list : int
            List of integers, representing the string index at which a desired
            string should be added. Desired string is concatenated to the original
            string at the given index position
        newLine : bool
            Says if the string to be added should be added as a newline after each
            index position

    Returns
    -------
        str
            Returns a concatenated string containing the originalString with stringToInsert concatenated at every index from listOfPositions
            If list is empty it returns the same string as the originalString
    """
    concatenatedString = originalString
    accumulator = 0
    stringToInsert = stringToInsert + '\n'
    if( newLine ):
        for index in listOfPositions:
            startOfIndex = accumulator + index
            newLineIndex = startOfIndex + concatenatedString[startOfIndex : ].find('\n') + 1
            concatenatedString = concatenatedString[ : newLineIndex] + stringToInsert + concatenatedString[newLineIndex : ]
            accumulator += len(stringToInsert)

    else:
        for index in listOfPositions:
            startOfIndex = accumulator + index
            concatenatedString = concatenatedString[ : startOfIndex] + stringToInsert + concatenatedString[startOfIndex : ]
            accumulator += len(stringToInsert)

    return concatenatedString

def getDoRegexIndecies(regex, givenString, storingList, globalIdx = 0):
    """
    Appends indecies of all the starting positions of matches for the given regex in the given string
    to the provided list reference.
    Parameters
    ----------
        regex : SRE_Pattern
            regular experssion which is used to parse the given string
        givenString : str
            string on which the regular expression will be used
        storingList : list
            List of found indecies

    Returns
    -------
        list : int
            Returns a list containing the string indecies of found matches from the given regex in the given string.
    """
    match = re.search(regex, givenString, re.MULTILINE | re.IGNORECASE)
    if( type(match) == type(None) ):
        #if not found return
        return
    # MatchIdxList = []
    #IDEA : For every match group do globalMatchStart = globalIdx + match.start(matchNum)
    # append to MatchIdxList
    #Then append to storingList
    indentation = " "*(match.end(1) - match.start(1))
    match2GlobalStart = globalIdx + match.start(2)
    match2GlobalEnd   = globalIdx + match.end(2)
    match3GlobalStart = globalIdx + match.start(3)
    match3GlobalEnd   = globalIdx + match.end(3)

    storingList.append( [indentation, [match2GlobalStart, match2GlobalEnd],[match3GlobalStart, match3GlobalEnd]])
    #The concatination of " " is needed to properly recognize a match group if it's exactly in the end
    # Containing string is in match.group() or match.group(0)
    getDoRegexIndecies(regex, match.group(0) +" ", storingList, globalIdx = globalIdx + match.start(0))
    getDoRegexIndecies(regex, givenString[match.end(3):], storingList, globalIdx = match3GlobalEnd)

#Main loop
if __name__ == '__main__':
    filesToDeclare = collectPaths()
    for filepath in filesToDeclare:
        #For every file:
        #Get the file code:
        #TODO :: get readFileString function here to assign test_str
        ###### FUNCTION #######
        with open(filepath, 'r') as file:
            print(f"\nOpening to read:{filepath}")
            test_str = file.read()
            print(f"Closed {filepath}")
        #############################
        #IF NO DO LOOP DETECTED GO TO NEXT FILE
        doLoopExists = re.search(regex, test_str, re.MULTILINE | re.IGNORECASE)
        if(type(doLoopExists) == type(None)):
            print(f"No old syntax DO LOOP detected in: {filepath}")
            continue
        # TODO :: Change to a for loop over all doidx
        #Get positions of all old DO statements
        #Group 1 -- indentation
        #Group 2 -- first Address of DO LOOP
        #Group 3 -- exit Address of DO LOOP
        doidx = []
        getDoRegexIndecies(regex, test_str, doidx)
        #All positions of DO Labels stored in doidx
        ##################################################################
		#Add END DO line as a comment (don't Change anything else)
        flagCommentEND_DO = "!END DO\n"
        #IDEA: Maybe faster to first create a list only of idxPair[2][1] and then give to function?
        for idxPair in doidx:
            commented_string = insertStrAtIndecies(flagCommentEND_DO, test_str, [idxPair[2][1]], newLine = True)
        ##################################################################
        #Write comments to file
        ########### FUNCTION ##################
        with open(filepath, 'w') as file:
            print(f"\033[1;35;42m Writing Comments to: {filepath} \033[0;37;40m")
            file.write(commented_string)
        #########################################
        #Compile and commit any assembly changes with message "changes from comments"
        #compile and SAVE asm diff from comment lines
        p = Path(f"{filepath}")
        #Get only filename for commits
        commitName = p.name
        fileName = p.name
        #convert9000.py hephaestus --withCMake | --withMake
        hephaestusString = f"python3 ~/development/codeConverter9000/converter9000.py hephaestus --withCMake --only={fileName}"
        #call sisyphus to compile asm
        print(hephaestusString)
        sp.call(hephaestusString, shell = True)

        #Check if program compiles
        if(not compileAndCheck( getMakeCommand() )):
            # Move outside of function
            print("Program did not compile")
            print('\a')
            input(f"Remove staged and unstaged changes from {commitName}. Press any key to continue to next file")
            break

        #Call git add to stage changes from comments
        gitCommentCommitArg = "git add -A"
        print("\033[1;32;40m " + gitCommentCommitArg + "\033[0;37;40m")
        sp.call(gitCommentCommitArg, shell=True)

        #Write END DO statement in the file
        flagEND_DO = 'END DO\n'
        #accumulator = 0
        #####
        # TODO :: For every DO Loop compile and check inside for loop, then the break will go to the next DO loop not the next file.
        for idxPair in doidx:
            #Replace first Address with whiteSpace
            test_str = insertInString(test_str, idxPair[1][0], idxPair[1][1], " "*(idxPair[1][1] - idxPair[1][0]))
            #Write END DO statement on a newline after the DO LOOP label
            test_str = insertStrAtIndecies(idxPair[0] + flagEND_DO, test_str, [idxPair[2][1]], newLine = True)
            ################ FUNCTION ########################
            with open(filepath, 'w') as file:
                print(f"\033[1;35;47m Updating DO statement in: {filepath} \033[0;37;40m")
                file.write(test_str)
            ###################################################
            #Save new assembly code after chaning DO LOOP
            print(hephaestusString)
            sp.call(hephaestusString, shell=True)
            #Check if program compiles
            #
            if(not compileAndCheck( getMakeCommand() )):
                print("\033[1;37;41m Program did not compile \033[0;37;40m")
                print('\a')
                input(f"Remove staged and unstaged changes from {commitName}. Press any key to continue to next file")
                break

            #Call GIT STATUS to check if there is assembly difference
            #Check for .asm after "changes not staged for commit:"
            if( detectUnstagedDifference("git status", "DumpedFiles", ".asm") ):
                print("\033[1;37;41m Detected assembly difference \033[0;37;40m")
                print('\a')
                input(f"Remove staged and unstaged changes from {commitName}. Press any key to continue to next file")
                break
            #Git commit -- this is after DO loop has been changed
            #Dirty way to just get ike/subfolder/filename.F90 for example
            #dirtyFilePath = filepath[filepath.index("athlet-cd/") + len("athlet-cd/"):]
            commitOnlyOneFile(filepath, message = f"Change DO_LOOP in {commitName}")
            #Wait 5 seconds just in case, for gitKraken to register any asm code change
            time.sleep(5)
