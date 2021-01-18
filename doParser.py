"""DoParser.py

Usage:
  DoParser.py declare <extension> (--withMake | --withCMake) [--path=<location> --version_Control_Command=<vc_add>] [--recursive | --only=<filename>...]

Commands:
  declare         Glob for the specified extension files and update DO LOOP for any file which uses the old DO 20 ... 20 last line syntax for DO LOOPS
Arguments:
  <extension>     Extension of files to declare variablse of. Should be '.f' or '.F90'
  <filename>      Name of the file to parse for DO LOOPS including the extension
Options:
  -p --path=<>    The path of the folder or files to change DO LOOPS in. Include last forward slash './path/to/folder/' [default: ./]

  --version_Control_Command=<>  Terminal command to execute in order to commit changes to .asm files when needed [default: git add -A]

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

regex = r"^(?!\!)(.*)?DO[ ]*?(?=\d+)(\d+)[\s\S]*?(?=\n(\d+))"
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
    except:
        warnings.warn("Warning: No .gitignore file found, cannot exclude paths not under version control in current folder")
        if(input("Do you wish to continue? y/n: ").upper() == 'Y'):
            pass
        else:
            raise SystemExit
    return paths


#Main loop
if __name__ == '__main__':
	filesToDeclare = collectPaths()
	for filepath in filesToDeclare:
		#For every file:
		#Get the file code:
		with open(filepath, 'r') as file:
			print(f"\nOpening to read:{filepath}")
			test_str = file.read()
		print(f"Closed {filepath}")
		#IF NO DO LOOP DETECTED GO TO NEXT FILE
		doLoopExists = re.search(regex, test_str, re.MULTILINE | re.IGNORECASE)
		if(type(doLoopExists) == type(None)):
			print(f"No old syntax DO LOOP detected in: {filepath}")
			continue
		#While there are labeled do loops
		while(type(doLoopExists != type(None) )):
			#Read latest file version
			with open(filepath, 'r') as file:
				test_str = file.read()
			#test_str is the file_string
			match = re.search(regex, test_str, re.MULTILINE | re.IGNORECASE)
			doidx = []

			#for matchNum, match in enumerate(matches):
			#Get positions of all old DO statements
			#print(f"matchNum: {matchNum}")
			#Group 1 -- indentation
			#Group 2 -- first Address of DO LOOP
			#Group 3 -- exit Address of DO LOOP
			indentation = " "*(match.end(1) - match.start(1))
			#FIND WHERE THE GOTO LABEL IS
			labelVal = match.group(2)
			labelRegex = r"^" + labelVal
			restOfString = test_str[match.end(2) : ]
			labelMatch = re.search(labelRegex, restOfString, re.IGNORECASE | re.MULTILINE)

			labelStart = int(match.end(2)) + int(labelMatch.start())
			labelEnd = int(match.end(2)) + int(labelMatch.end())
			if(type(labelMatch) == type(None)):
				warnings.warn(f"WARNING! Detected GOTO label {labelVal} could not be fouln with regex {labelRegex} after DO statement at {match.start(1)}")
				raise SystemExit

			doidx.append([indentation, [match.start(2),match.end(2)], [labelStart, labelEnd]])

			#Add END DO line as a comment (don't Change anything else)
			commented_string = test_str
			comment_accumulator = 0
			commentFlagEND_DO = "!END DO\n"
			for idxPair in doidx:
				#idxPair has indentation and index of first label at DO statement end second label where do GOES TO
				#idxPair = [" indentaion", [indexSTART,indexEND], [indexSTART, indexEND]]
				commentNewLineIdx = comment_accumulator + idxPair[2][1] + commented_string[comment_accumulator + idxPair[2][1] : ].find('\n') + 1

				commented_string = commented_string[ : commentNewLineIdx] + commentFlagEND_DO + commented_string[commentNewLineIdx : ]

				comment_accumulator += len(commentFlagEND_DO)

			#Write comments to file
			with open(filepath, 'w') as file:
				print(f"Writing Comments to: {filepath}")
				file.write(commented_string)

			#Compile and commit any assembly changes with message "changes from comments"
			#compile and SAVE asm diff from comment lines
	        #convert9000.py hephaestus --withCMake | --withMake
			p = Path(f"{filepath}")

			#Get only filename for commits
			commitName = Path(f"{filepath}").name
	        #CMake has object files named filename.F90.o , need to pass that to converter9000
			fileName = p.name + ".o"
			hephaestusString = f"python3 ~/development/codeConverter9000/converter9000.py hephaestus --withCMake --only={fileName}"
			print(hephaestusString)
			#call sisyphus to compile asm
			sp.call(hephaestusString, shell = True)

			#Call git add && git commit
			gitCommentCommitArg = f"git add -A && git commit -m 'Commit comment changes in {commitName}'"
			print(gitCommentCommitArg)
			sp.call(gitCommentCommitArg, shell=True)
			#Wait 5 seconds just in case, for gitKraken to register any asm code change
			time.sleep(5)


			flagEND_DO = 'END DO\n'
			accumulator = 0
			for idxPair in doidx:
				#Replace first Address with whiteSpace
				test_str = test_str[ : idxPair[1][0]] + " "*(idxPair[1][1] - idxPair[1][0]) + test_str[idxPair[1][1] : ]
				#Replace second Address with whiteSpace
				#test_str = test_str[ : idxPair[2][0]] + " "*(idxPair[2][1] - idxPair[2][0]) + test_str[idxPair[2][1] : ]
			#print("TEST STRING AFTER REMOVING DO ADDRESSES:")
			#print(test_str)

			for idxPair in doidx:
				#Line after last Do statement
				newLineIdx = accumulator + idxPair[2][1] + test_str[accumulator + idxPair[2][1]: ].find('\n') + 1
				test_str = test_str[ : newLineIdx] + idxPair[0] + flagEND_DO + test_str[newLineIdx : ]
				accumulator += len(idxPair[0]) + len(flagEND_DO)
			#print("TEST STRING AFTER ADDING END DO STATEMENT:")
			#print(test_str)
			#TODO::: CODE GETS CUT UP WRONG
			with open(filepath, 'w') as file:
				file.write(test_str)
			#Save new assembly code after chaning DO LOOP
			print(hephaestusString)
			sp.call(hephaestusString, shell = True)

			#Git commit -- this is after DO loop has been changed
			gitCommitArg = f"git add -A && git commit -m 'Change DO_LOOP in {commitName}'"
			print(gitCommitArg)
			sp.call(gitCommitArg, shell = True)
			#Wait 5 seconds just in case, for gitKraken to register any asm code change
			time.sleep(5)
			#####################################
			# Check if there are SUB DO loops with labels
			doLoopExists = re.search(regex, test_str, re.MULTILINE | re.IGNORECASE)
			if(type(doLoopExists) == type(None)):
				input("No more DO LOOPS detected, press any key to go to next file")
			else:
				input("More DO LOOPs detected, press any key to continue.")
		print(f"Finished DO LOOP update in {filepath}")
