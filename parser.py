"""Parser.py

Usage:
  parser.py declare <extension> (--withMake | --withCMake) [--path=<location> --version_Control_Command=<vc_add>] [--recursive | --only=<filename>...]

Commands:
  declare         Glob for the specified extension files and declare variables for any file which uses implicit double precision
Arguments:
  <extension>     Extension of files to declare variablse of. Should be '.f' or '.F90'
  <filename>      Name of the file to parse for type declaration including the extension
Options:
  -p --path=<>    The path of the folder or files to do type declaration on. Include last forward slash './path/to/folder/' [default: ./]

  --version_Control_Command=<>  Terminal command to execute in order to commit changes to .asm files when needed [default: git add -A]

  -r --recursive  If specified the program will run recursively

  -o --only <name1,name2>   Only convert the given files or files seperated by comma. Include file extension. For example '-o file1.txt,file2.cpp,file3.f...'

  --withMake                Specify if you want to also run a make command to build the project, compiling any changed file. Should be careful if running it with sisyphus downhill as if helper '_.f90' files are not deleted they will compile and create redundant object files. [default: False]

  --withCMake              Specify if the files are built using CMake instead of make. compiling any changed file. Should be careful if running it with sisyphus downhill as if helper '_.f90' files are not deleted they will compile and create redundant object files. [default: False]
"""
#--path --recursive <extension> --only
#
import fnmatch
import warnings
from docopt import docopt
from glob import glob
import re
import TypeTemplate as tmp
import subprocess as sp
from pathlib import Path
args = docopt(__doc__, version = '2.0')
# <parse> [--only --recursive:default --control_version_comand:git add -A && git commit default]

#Can replace DIMENSION with any keyword
#Detects DIMENSION declaration and all line continuations in group 1
#dimensionPattern = r"DIMENSION(?=((.*\&\s*\n\s*\&)*.*\n?))"
##Assuming that there is only one DIMENSION declaration
pars_DIMENSION = re.compile(r"^(?!.*?\!)\s*?DIMENSION(?=((.*\&\s*\n\s*\&)*.*\n?))(?!.+(\s+\:))",flags = re.IGNORECASE | re.MULTILINE)
#pars_DIMENSION:
#   Group1 : All variables after DIMENSION declaration including last continued line
# Group2 : All variables after Dimension Declaration up to the last '&' symbol (at begining of last line)

#Detect variabels from Dimension string: anything name(dim1,...,dimN)
pars_Vars = re.compile(r"[\w\s]*\(.*?\)+")
#Detect IMPLICIT DOUBLE PRECISION declaration
pars_implicit_Double_declaration = re.compile(r"^(?!.*?\!).*(IMPLICIT.*DOUBLE.*PRECISION.*\n)", flags = re.IGNORECASE | re.MULTILINE)

#######Special character for undeclared variable type: ‘ and ’

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
        #Ignore files from .gitignore
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
def insertInString(originalString, cutIndex1, cutIndex2, stringToInsert):
    """Insert 'stringToInsert' between cutIndex1 and cutIndex2 of the given string 'originalString' returning originalstring[:cutIndex1] + stringToInsert + originalString[cutIndex2:]
     """
    return originalString[:cutIndex1] + stringToInsert + originalString[cutIndex2:]

if __name__ == '__main__':
    filesToDeclare = collectPaths()
    for filepath in filesToDeclare:
        with open(filepath,'r') as file:
            print(f"\nOpening to read: {filepath}")
            fileString = file.read()
        print(f"Closed {filepath}")
        ##########################################
        #FIND IMPLICIT DOUBLE PRECISION STATEMENT
        ##########################################
        implicitDeclaration = pars_implicit_Double_declaration.search(fileString)
        if(type(implicitDeclaration) == type(None)):
            #If no IMPLICIT DOUBLE DECLARATION, skip file
            print(f"No IMPLICIT DOUBLE declaration in {filepath}")
            continue
        #Create a template
        template = tmp.TypeTemplate()
        #get postiion of IMPLICIT DOUBLE PRECISION
        #contained in the first matching group
        implicitLineStartIdx = implicitDeclaration.start(0)
        implicitStartIdx = implicitDeclaration.start(1)
        implicitEndIdx = implicitDeclaration.end(1)
        #Get the indentation of the IMPLICIT DOUBLE declaration
        indentationIdx = implicitStartIdx - fileString[:implicitStartIdx].rfind("\n") -1
        #Pass the detected indentaion to the template class
        template.indentation = indentationIdx
        ###########################################
        #FIND DIMENSION DECLARATION
        ##########################################
        dimensionLine = pars_DIMENSION.search(fileString)
        #IF a DIMENSION declaration is detected
        dimensionCommentIdx = [] #[[idxToAddComment1, ... idxToAddCommentN], ... ,[ ==//==]]
        if(type(dimensionLine) != type(None)):
            if(implicitLineStartIdx > dimensionLine.start(0)):
                #Make sure DIMENSION declaration is after IMPLICIT declaration, its assumed later when writing to the file
                warnings.warn("Warning, DIMENSION declaration detected before IMPLICIT declaration. Cannot proceed as script requires IMPLCIT declaration to be first when writing.")
                raise SystemExit

            #FOR EVERY DIMENSION DECLARATION:
            dimensionMatches = pars_DIMENSION.finditer(fileString)
            for matchNum , match in enumerate(dimensionMatches):
                #Save the idx of where comments need to be inserted
                #Add start index at start of line of DIMENSION
                dimString = fileString[:match.start(1)]
                dimensionCommentIdx.append( dimString.rfind('\n') + 1 )

                #In the declared Dimensions find all new lines and add the next index to the list. Exclude last '\n' from the string
                for idx,letter in enumerate(match.group(1)[:-1]):
                    if(letter == '\n'):
                        dimensionCommentIdx.append(match.start(1) + idx + 1)
                ##dimensionCommentIdx now has all indecies to put a comment at
                #get variabels inside DIMENSION declaration string
                variablesMatch = pars_Vars.findall(match.group(1))
                #Parse found variablse to remove any whitespace
                for idx, var in enumerate(variablesMatch):
                    #Remove all meaningless empty lines to have varibale list be in the form:
                    #[NaMe(ImAX,ZtOpMAX), NAMe2(DiM1,Dim2)]
                    variablesMatch[idx] = var.replace(" ","")
                for var in variablesMatch:
                    #add detected variables to the tempalte. The Template class handles converting to upper case and parsing different dimensions and keywords. Takes variables of the form Name(Dim1,Dim2...) or just Name
                    template.addVariable(var)

            ############################################
            #Comment out DIMENSION Declaration in TEMPLATE
            template.commentToggleTemplate()
            ############################################
        else:
            #If There is no DIMENSION found but there is IMPLICIT DOUBLE, continue with the type declaration.
            pass

        with open(filepath,'w') as file:
            #Dimensions are commented out, old dimension declaration is stil there
            ## NOTE --> It doesn't compile if DIMENSION(X) is before PARAMATER X = ... is declared, also some files might have multiple Dimension declarations with just one variable.
            print(f"\nWriting commented out template to: {filepath}")
            writeString = insertInString(fileString, implicitLineStartIdx, implicitEndIdx, template.getTemplate())
            file.write(writeString)
        print(f"Closed {filepath}\n")
        #compile and SAVE asm diff from comment lines
        #convert9000.py hephaestus --withCMake | --withMake
        p = Path(f"{filepath}")
        #CMake has object files named filename.F90.o , need to pass that to converter9000
        fileName = p.name + ".o"
        hephaestusString = f"python3 ~/development/codeConverter9000/converter9000.py hephaestus --withCMake --only={fileName}"
        print(hephaestusString)

        sp.call(hephaestusString, shell = True)
        ###########################################
        #STAGE ANY ASM DIFFERENCES FROM COMMENTS
        ###########################################
        #DEBUGING: wait for user to check
        #input("Check how well script added commented template: Press any key to continue")
        terminalargs = "git add -A"
        sp.call(terminalargs, shell = True)

        #######################################################
        #Switch to Implicit none to gather undeclared variabels
        #######################################################
        #comment old dimension declarations in filestring and write to file
        if(len(dimensionCommentIdx) > 0):
            comment_accumulator = 0
            for commentidx in dimensionCommentIdx:
                commentidx += comment_accumulator
                fileString = insertInString(fileString,commentidx,commentidx,"!")
                comment_accumulator += len("!")

        #NOTE: Not needed to write and read, can just continue working with fileSTring
        
        #Presumably now all DIMENSION lines are commented out
        with open(filepath, 'w') as file:
            file.write(fileString)

        ###################################################
        # Re evaluate implicit declaration index
        with open(filepath, 'r') as file:
            fileString = file.read()
        #
        implicitDeclaration = pars_implicit_Double_declaration.search(fileString)
        #get postiion of IMPLICIT DOUBLE PRECISION
        #contained in the first matching group
        implicitLineStartIdx = implicitDeclaration.start(0)
        implicitStartIdx = implicitDeclaration.start(1)
        implicitEndIdx = implicitDeclaration.end(1)
        #################################################

        #Uncomment Dimension declarations
        template.commentToggleTemplate()
        #Switch comments on IMPLICIT DOUBLE and IMPLICIT NONE
        template.switchImplicitStatement()
        with open(filepath,'w') as file:
            print(f"\nSwitching to Implicit none: {filepath}")
            writeString = insertInString(fileString, implicitLineStartIdx, implicitEndIdx, template.getTemplate())
            file.write(writeString)
        print(f"Closed {filepath}\n")


        print("\nCompiling with IMPLICIT NONE statement to get undeclared variables\n")
        detectedVariables = []
        compileArgs = getMakeCommand()
        proc = sp.Popen(compileArgs, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
        for line in proc.stdout.readlines():
            line = line.decode("utf-8")
            print(line)
            if("Error" in line and "‘" in line and "’" in line and "IMPLICIT type" in line):
                variableName = line[line.index("‘")+1 : line.index("’")]
                detectedVariables.append(variableName)
        print(f"Detected undeclared varaibels:\n {detectedVariables}\n")
        for variable in detectedVariables:
            template.addVariable(variable)
        with open(filepath,'w') as file:
            print(f"Writing declared type variables to: {filepath}")
            writeString = insertInString(fileString, implicitLineStartIdx, implicitEndIdx, template.getTemplate())
            file.write(writeString)
        print(f"Closed {filepath}")
        #print("Compiling program after Type Declaration and saving overwriting assembly code:")
        ###########################################################
        #Compile to check for undeclared functions
        ###########################################################
        print("\nCompiling with IMPLICIT NONE statement to get undeclared functions\n")
        detectedVariables = []
        compileArgs = getMakeCommand()
        proc = sp.Popen(compileArgs, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
        for line in proc.stdout.readlines():
            line = line.decode("utf-8")
            print(line)
            #IDEA :: Add 'and IMPLICIT type' to more thoroughly check erro message
            if("‘" in line and "’" in line and "IMPLICIT type" in line):
                variableName = line[line.index("‘")+1 : line.index("’")]
                detectedVariables.append(variableName)
        print(f"Detected undeclared functions:\n {detectedVariables}\n")
        for variable in detectedVariables:
            template.addVariable(variable)
        ################################################################
        #Write type template to file with IMPLICIT NONE
        #############################################################
        with open(filepath,'w') as file:
            print(f"Writing declared type functions to: {filepath}")
            writeString = insertInString(fileString, implicitLineStartIdx, implicitEndIdx, template.getTemplate())
            file.write(writeString)
        print(f"Closed {filepath}")
        print("Compiling program after Type Declaration and saving overwriting assembly code:")
        ################################################################
        #Overwrite ASM code and wait for input to continue
        ###############################################################
        sp.call(hephaestusString, shell = True)
        print('\a')
        input(f"Check {filepath} to see how well the script did")
