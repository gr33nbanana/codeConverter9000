"""typeParser.py

Usage:
  typeParser.py declare <extension> (--withMake | --withCMake) [--path=<location> --version_Control_Command=<vc_add>] [--recursive | --only=<filename>...]

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
    """"
    Return a string of the relevant terminal command to compile the program, depending on if --withMake or --withCMake was specified

    Return
    ------
        str
            A string of the bash command to compile the program
    """

    if(args['--withMake']):
        return "make built"
    elif(args['--withCMake']):
        return "cd _build && make"

def compileFiles():
    """
    Calls the make or CMake command line for compiling the project.
    """
    if(args['--withMake']):
        sp.call("make built", shell = True)
    elif(args['--withCMake']):
        sp.call("cd _build && make", shell= True)

def collectPaths(location = args['--path'], fromType = args['<extension>']):
    """Returns a list of all files in the specified --path with the specified extension <extension>

    Parameters
    ----------
        location : str
            Root of where collection of Paths starts.
        fromType : str
            File extension to look for and collect all paths ending with it.

    Returns
    -------
        list
            List of all found paths

    Example
    -------
        collectPaths(fromType = '.F90')
        collectPaths(location = './folder/', fromType = '.F90')
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
    except Exception:
        warnings.warn("Warning: No .gitignore file found, cannot exclude paths not under version control in current folder")
        if(input("Do you wish to continue? y/n: ").upper() == 'Y'):
            pass
        else:
            raise SystemExit
    return paths
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
        Returns a concatenated string = originalstring[:cutIndex1] + stringToInsert + originalString[cutIndex2:]
     """
    return originalString[:cutIndex1] + stringToInsert + originalString[cutIndex2:]

def locateAndDeclareDimensions(filestring, template, dimensionParser):
    """
    Function parses the filestring to find all DIMENSION declarations.
    It saves the indecies of the start of the lines of the declarations
    in a list. Then it passes the declared names to the template to handle
    their type declaration and calls the method to comment them out.
    Returns a list of all the indecies where
    a comment symbol should be added to comment out the old declartions.

    Parameters
    ----------
        filestring : str
            String containing the text of the file from filepath
        template : TypeTemplate
            the template which contains and handles the type declaration of
            the found arrays
        dimensionParser : SRE_Pattern
            A compiled regex object which is used to find all instances of
            DIMENSION declarations and it's line continuations in the filestring

    Returns
    -------
        list
            A list of indecies where a comment should be added in order
            to comment out all old DIMENSION declarations and their
            line continuations
    """
    indeciesToComment = []
    #FOR EVERY DIMENSION DECLARATION:
    dimensionMatches = dimensionParser.finditer(fileString)
    for matchNum , match in enumerate(dimensionMatches):
        #Save the idx of where comments need to be inserted
        #Add start index at start of line of DIMENSION
        dimString = fileString[:match.start(1)]
        indeciesToComment.append( dimString.rfind('\n') + 1 )

        #In the declared Dimensions find all new lines and add the next index to the list. Exclude last '\n' from the string
        for idx,letter in enumerate(match.group(1)[:-1]):
            if(letter == '\n'):
                indeciesToComment.append(match.start(1) + idx + 1)
        ##indeciesToComment now has all indecies to put a comment at
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
    return indeciesToComment

def switchToImplicitNoneStatement(filepath, fileString, dimensionCommentIdx, template, implicitDoubleParser):
    """
    Changes the IMPLICIT declaration in the provided Fortran file
    to an IMPLICIT NONE.
    First the function comments out all DIMENSION declarations and
    overwrites the file. Then it switches the IMPLICIT declaration
    in the template and writes it in the file.

    Parameters
    ----------
        filepath : str
            The full path and name of the file.
        filestring : str
            The string containing the text inside the file
        dimensionCommentIdx : list
            A list of all the indecies where a comment symbol '!' should be placed,
            in the fileString.
        template : TypeTemplate
            The template object which contains and handles the type declaration of
            variable names, and handles switching implicit statements and
            commenting out or uncomennting the template when necessary.
        implicitDoubleParser : SRE_Pattern
            A compiled regex object which is used to parse for an "IMPLICIT DOUBLE (A-H,O-Z) type declaration in the fortran file

    """
    ###################################################
    # Re evaluate implicit declaration index just to be safe
    #fileString = readFileString(filepath, message=f"Reading {filepath} after commenting out DIMENSIONS")
    #with open(filepath, 'r') as file:
    #    fileString = file.read()
    #
    #implicitDeclaration = implicitDoubleParser.search(fileString)
    #get postiion of IMPLICIT DOUBLE PRECISION
    #contained in the first matching group
    #implicitLineStartIdx = implicitDeclaration.start(0)
    #implicitStartIdx = implicitDeclaration.start(1)
    #implicitEndIdx = implicitDeclaration.end(1)
    #################################################

    #Uncomment Dimension declarations
    #TODO :: change to template.uncommentAllTemplate()
    template.commentToggleTemplate()
    #Switch comments on IMPLICIT DOUBLE and IMPLICIT NONE
    template.switchImplicitStatement()
    writeString = insertInString(fileString, implicitLineStartIdx, implicitEndIdx, template.getTemplate())
    writeFileString(filepath, writeString, message = f"\nSwitching to IMPLICIT NONE in: {filepath}")

def compileForVariables(compileArgument, template, message = None):
    """
    Compiles the program and reads through the output of the terminal.
    If there are: ' Error ', ' ‘ ', ' ’ ', ' IMPLICIT type ' in the terminal line
    it will pass the name of the variable between the apostrophes to the template
    to declare it's type.

    Parameters
    ----------
        compileArgument : str
            string of bash command line to execute for compilation
        template : TypeTemplate
            the template class which stores and handles the undeclared
            variables
        message : str
            Information message to print out to the terminal
    """
    if(type(message) != type(None)):
        print(message)

    detectedVariables = []
    proc = sp.Popen(compileArgument, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
    for line in proc.stdout.readlines():
        line = line.decode("utf-8")
        print(line)
        if("Error" in line and "‘" in line and "’" in line and "IMPLICIT type" in line):
            variableName = line[line.index("‘")+1 : line.index("’")]
            detectedVariables.append(variableName)
    print(f"Detected undeclared variables or functions: {detectedVariables}")
    for variable in detectedVariables:
        template.addVariable(variable)


def readFileString(filepath, message = None):
    """
    Opens and reads the provided filepath and returns a string of the contents of the file

    Parameters
    ----------
        filepath : str
            The full path and name of the file to read.
        message : str
            Message to print out to the terminal for information

    Returns
    -------
    str
        String containing the information in the file.
    """
    if(type(message) != type(None)):
        print(message)
    with open(filepath, 'r') as file:
        redString = file.read()
    print(f"Closed {filepath}")
    return redString

def writeFileString(filepath, stringToWrite, message = None):
    """
    Opens a file and overwrites it's contents with the priveded string

    Parameters
    ----------
        filepath : str
            Full path and name to the file to be overwritten
        stringToWrite : str
            String which will be written to the file.
            This will become the new contents of the file.
        message : str
            Message to print out to the Terminal for Information
    """
    if(type(message) != type(None)):
        print(message)
    with open(filepath, 'w') as file:
        file.write(stringToWrite)
    print(f"Closed{filepath}")

if __name__ == '__main__':
    filesToDeclare = collectPaths()
    for filepath in filesToDeclare:
        fileString = readFileString(filepath, message = f"Opening to read {filepath}")
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
        #Used for inserting the template between these two indecies
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
        dimensionCommentIdx = []
        #IF a DIMENSION declaration is detected
        if(type(dimensionLine) != type(None)):
            #If there are declared dimensions in the file.
            if(implicitLineStartIdx > dimensionLine.start(0)):
                #Make sure DIMENSION declaration is after IMPLICIT declaration, its assumed later when writing to the file
                warnings.warn("Warning, DIMENSION declaration detected before IMPLICIT declaration. Cannot proceed as script requires IMPLCIT declaration to be first when writing.")
                raise SystemExit

            dimensionCommentIdx = locateAndDeclareDimensions(fileString, template, dimensionParser = pars_DIMENSION) #[[idxToAddComment1, ... idxToAddCommentN], ... ,[ for each dimension declaration ==//==]]
        else:
            #If There is no DIMENSION found but there is IMPLICIT DOUBLE, continue with the type declaration.
            pass

        #############################
        # Add Type template as comment lines in order to save any asm difference coming from just changing the number of lines
        # Template is commneted out!
        #IDEA: Can change workflow to use the commentAll and uncommentAll methods of the template, in order to not keep track of the state.
        #############################
        writeString = insertInString(fileString, implicitLineStartIdx, implicitEndIdx, template.getTemplate())
        writeFileString(filepath, writeString, message = f"\nWriting commented out template to : {filepath}")
        #compile and SAVE asm diff from comment lines
        #convert9000.py hephaestus --withCMake | --withMake
        p = Path(f"{filepath}")
        #CMake has object files named filename.F90.o , need to pass that to converter9000
        fileName = p.name
        hephaestusString = f"python3 ~/development/codeConverter9000/converter9000.py hephaestus --withCMake --only={fileName}"
        print(hephaestusString)
        sp.call(hephaestusString, shell = True)

        ###########################################
        #STAGE ANY ASM DIFFERENCES FROM COMMENTS
        ###########################################
        sp.call("git add -A", shell = True)

        #comment old dimension declarations in filestring and write to file
        if(len(dimensionCommentIdx) > 0):
            comment_accumulator = 0
            for commentidx in dimensionCommentIdx:
                commentidx += comment_accumulator
                fileString = insertInString(fileString, commentidx, commentidx,"!")
                comment_accumulator += len("!")

        #NOTE: Not needed to write and read, can just continue working with fileSTring

        # Now all DIMENSION lines are commented out
        writeFileString(filepath, fileString, message= "\nCommenting out old DIMENSION declarations")
        #######################################################
        #Switch to IMPLICIT NONE statement
        #######################################################
        switchToImplicitNoneStatement(filepath, fileString, dimensionCommentIdx, template, implicitDoubleParser = pars_implicit_Double_declaration)
        # Re evaluate implicit declaration index
        #Optional, done just in case.
        #fileString = readFileString(filepath, message = f"Opening to read {filepath}")
        #
        #implicitDeclaration = pars_implicit_Double_declaration.search(fileString)
        #implicitLineStartIdx = implicitDeclaration.start(0)
        #implicitStartIdx = implicitDeclaration.start(1)
        #implicitEndIdx = implicitDeclaration.end(1)

        #################################################
        # Compile to gather undeclared variable names
        #################################################
        compileForVariables(getMakeCommand(), template, message = "Compiling with IMPLICIT NONE statement to get udneclared variables\n")

        writeString = insertInString(fileString, implicitLineStartIdx, implicitEndIdx, template.getTemplate())
        writeFileString(filepath, writeString, message = f"Writing declared type variables to: {filepath}")

        ###########################################################
        #Compile to check for undeclared functions
        ###########################################################
        compileForVariables( getMakeCommand(), template, message = "\nCompiling with IMPLICIT NONE satement to get udneclared functions\n")

        writeString = insertInString(fileString, implicitLineStartIdx, implicitEndIdx, template.getTemplate())
        writeFileString(filepath, writeString, message = f"Writing declared type functions to: {filepath}")

        print("Compiling program after Type Declaration and overwriting assembly code:")
        ################################################################
        #Overwrite ASM code and wait for input to continue
        ###############################################################
        sp.call(hephaestusString, shell = True)
        print('\a')
        input(f"Check {filepath} to see how well the script did")
