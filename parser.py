#TODO::docopt string here
"""Parser.py

Usage:
  parser.py declare <extension> (--withMake | --withCMake) [--path=<location> --version_Control_Command=<vc_add>] [--recursive | --only=<filename>...]

Commands:
  declare         Glob for the specified extension files and declare variables for any file which uses implicit double precision
Arguments:
  <extension>     Extension of files to declare variablse of. Should be '.f' or '.f90'
  <filename>      Name of the file to parse for type declaration including the extension
Options:
  -p --path=<>    The path of the folder or files to do type declaration on. Include last forward slash './path/to/folder/' [default: ./]

  --version_Control_Command=<>  Terminal command to execute in order to commit changes to .asm files when needed [default: git add -A]

  -r --recursive  If specified the program will run recursively

  -o --only <name1,name2>   Only convert the given files or files seperated by comma.Include file extension.For example '-o file1.txt,file2.cpp,file3.f...'

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
args = docopt(__doc__, version = '1.0')
# <parse> [--only --recursive:default --control_version_comand:git add -A && git commit default]

#Can replace DIMENSION with any keyword
#Detects DIMENSION declaration and all line continuations in group 1
#dimensionPattern = r"DIMENSION(?=((.*\&\s*\n\s*\&)*.*\n?))"
##Assuming that there is only one DIMENSION declaration
pars_DIMENSION = re.compile(r"^(?!\!).*?DIMENSION(?=((.*\&\s*\n\s*\&)*.*\n?))(?!.+(\s+\:))",flags = re.IGNORECASE | re.MULTILINE)
#Detect variabels from Dimension string: anything name(dim1,...,dimN)
pars_Vars = re.compile(r"[\w\s]*\(.*?\)")
#Detect IMPLICIT DOUBLE PRECISION declaration
pars_implicit_Double_declaration = re.compile(r".*IMPLICIT.*DOUBLE.*PRECISION.*\n")
#TODO :: create parser for 'undeclared type' of a variable for stderr/stdout

#######Special character for undeclared variable type: ‘ and ’

#TODO :: Seperate running the make file and parsing the error message for variables from the main loop to be able to do it independantly (eg. Fix something by hand with the Dimensions, then just run it for variables.)



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

if __name__ == '__main__':
    filesToDeclare = collectPaths()
    for filepath in filesToDeclare:
        with open(filepath,'r') as file:
            print(f"Opening to read: {filepath}")
            fileString = file.read()
        print(f"Closed {filepath}")
        #find DIMENSION declaration
        dimensionLine = pars_DIMENSION.search(fileString)
        #get variabels inside DIMENSION declaration string
        variablesMatch = pars_Vars.findall(dimensionLine.group(1))
        #get postiion of IMPLICIT DOUBLE PRECISION
        #contained in the first matching group
        implicitDeclaration = pars_implicit_Double_declaration.search(fileString)
        if(type(implicitDeclaration) == type(None)):
            print(f"No IMPLICIT DOUBLE declaration in {filepath}")
            continue
        implicitStartIdx = implicitDeclaration.start(0)
        implicitEdnIdx = implicitDeclaration.end(0)

        #Get the indentation of the DIMENSION declaration
        indentationIdx = dimensionLine.start(0) - fileString[:dimensionLine.start(0)].rfind("\n") -1

        #Parse found variablse to remove any whitespace
        for idx, var in enumerate(variablesMatch):
            #Remove all meaningless empty lines to have varibale list be in the form:
            #[NaMe(ImAX,ZtOpMAX), NAMe2(DiM1,Dim2)]
            variablesMatch[idx] = var.replace(" ","")

        #Create a template and give it the detected indentation
        template = tmp.TypeTemplate()
        #Pass the detected indentaion to the template class
        template.indentation = indentationIdx
        for var in variablesMatch:
            #add detected variables to the tempalte. The Template class handles converting to upper case and parsing different dimensions and keywords. Takes variables of the form Name(Dim1,Dim2...) or just Name
            template.addVariable(var)

        with open(filepath,'w') as file:
            #TODO:: check if its ok that only type lines are commented, dimensions are uncomentted
            ## --> It doesn't compile if DIMENSION(X) is before PARAMATER X = ... is declared, also some files might have multiple Dimension declarations with just one variable.
            print(f"Writing commented out template to: {filepath}")
            #Remove previous dimension declaration
            writeString = fileString[:dimensionLine.start(0)] + fileString[dimensionLine.end(1):]
            writeString = fileString[:implicitStartIdx] + template.getTemplate() + fileString[implicitEdnIdx:]
            file.write(writeString)
        print(f"Closed {filepath}")
        #compile and SAVE asm diff from comment lines
        #convert9000.py hephaestus --withCMake | --withMake
        sp.call("python3 ~/development/codeConverter9000/converter9000.py hephaestus --withCMake", shell = True)
        #TODO:: change getting terminalargs from docopt
        terminalargs = "git add -A"
        sp.call(terminalargs, shell = True)

        template.switchImplicitStatement()
        template.commentToggleTemplate()
        with open(filepath,'w') as file:
            print(f"Switching to Implicit none and uncommenting template of: {filepath}")
            #Remove previous dimension declaration
            writeString = fileString[:dimensionLine.start(0)] + fileString[dimensionLine.end(1):]
            writeString = fileString[:implicitStartIdx] + template.getTemplate() + fileString[implicitEdnIdx:]
            file.write(writeString)
        print(f"Closed {filepath}")


        #TODO::run compilation and parse error message
        print("Compiling with IMPLICIT NONE statement to get undeclared variables")
        detectedVariables = []
        compileArgs = getMakeCommand()
        proc = sp.Popen(compileArgs, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
        for line in proc.stdout.readlines():
            line = line.decode("utf-8")
            if("‘" and "’" in line):
                variableName = line[line.index("‘")+1 : line.index("’")]
                detectedVariables.append(variableName)
        for variable in detectedVariables:
            template.addVariable(variable)
        with open(filepath,'w') as file:
            print(f"Writing declared type variables to: {filepath}")
            #Remove previous dimension declaration
            writeString = fileString[:dimensionLine.start(0)] + fileString[dimensionLine.end(1):]
            writeString = fileString[:implicitStartIdx] + template.getTemplate() + fileString[implicitEdnIdx:]
            file.write(writeString)
        print(f"Closed {filepath}")
        print("Compiling program after Type Declaration:")
        sp.call(compileArgs, shell = True)
        input(f"Check {filepath} to see how well the script did")


        #TODO::either add one by one or in group
#%% Hydrogen test
