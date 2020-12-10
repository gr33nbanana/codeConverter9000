"""ifParser.py

Usage:
  ifParser.py parse <extension> [--path=<location>] [--recursive | --only=<filename>...]

Commands:
  parse    Go through specified files and change arithmetic IF commands to normal IF THEN statements.

Arguments:
  <extension>    The extension with which glob finds the files to parse through. E.g. '.F90'
  <filename>     Name of the file to parse for arithmetic IF statements, should include the extension.

Options:
  -p --path=<>               The path of the folder or files to parse through. Include last forward slash './path/to/folder/' [default: ./]

  -r --recursive             If specified the program will run recursively

  -o --only <name1,name2>    Only convert the given files or files seperated by comma.Include file extension.For example '-o file1.txt,file2.cpp,file3.f...'

"""

import re
from docopt import docopt
from glob import glob
import fnmatch
import warnings

args = docopt(__doc__, version = '1.0')
#Parser to find arithmetic IF statemetns
ifParser = re.compile(r"^(?!\!).+(IF\s*?\(.*?\))\s*?(\d+),(\d+),(\d+)  ", re.IGNORECASE | re.VERBOSE | re.MULTILINE )

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
        warnings.warn("Warning: No .gitignore file found, cannot exclude files not under version control in current folder")
    return paths

def ifWriter(indent: int, statement: str, value1: str, value2: str, value3: str) -> str:
    """indent: Indentation of the statement (how many spaces)at begining of line. The statement is not returned indented, it should be overwritten at the start of its current position.

    statement: Arithmetic IF statement to rewrite ('IF(expresion)').

    value1, value2, value3: Values of arithmetic IF for < 0, == 0, > 0 respectively.

    Returns a string to overwrite the file string between the start of line and end index of the current arithmetic If expression filestring[ line.start() : match.end()]"""
    #Depending on the regex used to parse the file the first IF() statement might not need to be indented. If Multiline is used in the parser, you need indentation, else you don't.
    returnStr = ''
    #if v1 == v2  IF (A <= 0)
    #group(1)[:-1] + '<= 0)'
    #elif V2 == v3 IF (a <  0)
    #else IF(a <0) IF (a == 0) if (a > 0)
    if(value1 == value2):
        #Less or equal to 0
        statement = statement[:-1] + ' <= 0) THEN\n'

        returnStr = " "*indent + f"{statement}" + " "*(indent + 2) + f"GOTO {value1}\n" + " "*indent + "ELSE\n" + " "*(indent + 2) + f"GOTO {value3}\n"+ " "*indent +"END IF\n"
    elif(value2 == value3):
        statement = statement[:-1] + ' < 0) THEN\n'

        returnStr = " "*indent + f"{statement}" + " "*(indent + 2) + f"GOTO {value1}\n" + " "*indent + "ELSE\n" + " "*(indent + 2) + f"GOTO {value3}\n"+ " "*indent +"END IF\n"
    else:
        statement1 = statement[:-1] + ' < 0) THEN\n'
        statement2 = statement[:-1] + ' == 0) THEN\n'

        returnStr = " "*indent + f"{statement1}" + " "*(indent + 2) + f"GOTO {value1}\n" + " "*indent + f"ELSE {statement2}" + " "*(indent + 2) + f"GOTO {value2}\n" + " "*indent +"ELSE\n" + " "*(indent + 2) + f"GOTO {value3}\n" + " "*indent + "END IF\n"
    return returnStr

if __name__ == '__main__':
    if(args['parse']):
        filesToParse = collectPaths()
        for filePath in filesToParse:
            print(f"Parsed: {filesToParse.index(filePath) + 1} / {len(filesToParse)} files")
            with open(filePath, 'r') as file:
                #print(f"Parsing {filePath}")
                fileString = file.read()

            matches = ifParser.finditer(fileString)
            ifList = []
            for matchNum , match in enumerate(matches):
                indent = match.start(1) - fileString[:match.start(1)].rfind("\n") - 1

                ifStatementString = ifWriter(indent, match.group(1), match.group(2), match.group(3), match.group(4))

                ifList.append([match.start(0),match.end(4), ifStatementString])

            accumulator = 0
            writeString = fileString
            for statement in ifList:
                with open(filePath, 'w') as file:
                    writeString = writeString[:statement[0] + accumulator] + statement[2] + writeString[statement[1] + accumulator:]
                    file.write(writeString)
                accumulator += len(statement[2]) - (statement[1] - statement[0])
#%% test fnmatch
