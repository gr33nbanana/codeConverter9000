import re
import TypeTemplate as tmp
#TODO :: Add docopt interface
# <parse> [--only --recursive:default --control_version_comand:git add -A && git commit default]

#Can replace DIMENSION with any keyword
#Detects DIMENSION declaration and all line continuations in group 1
#dimensionPattern = r"DIMENSION(?=((.*\&\s*\n\s*\&)*.*\n?))"
##Assuming that there is only one DIMENSION declaration
pars_DIMENSION = re.compile(r"DIMENSION(?=((.*\&\s*\n\s*\&)*.*\n?))",flags = re.IGNORECASE)
#Detect variabels from Dimension string: anything name(dim1,...,dimN)
pars_Vars = re.compile(r"[\w\s]*\(.*?\)")
#Detect IMPLICIT DOUBLE PRECISION declaration
pars_implicit_Double_declaration = re.compile(r".*IMPLICIT.*DOUBLE.*PRECISION.*\n")

#TODO :: get filepath as argument
filepath = './.tests/evdata.f90'
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
implicitStartIdx = implicitDeclaration.start(0)
implicitEdnIdx = implicitDeclaration.end(0)

#Get the indentation of the DIMENSION declaration
indentationIdx = dimensionLine.start(0) - fileString[:dimensionLine.start(0)].rfind("\n") -1

for idx, var in enumerate(variablesMatch):
    #Remove all meaningless empty lines to have varibale list be in the form:
    #[NaMe(ImAX,ZtOpMAX), NAMe2(DiM1,Dim2)]
    variablesMatch[idx] = var.replace(" ","")

#Create a template and give it the detected indentation
template = tmp.TypeTemplate()
#Pass the detected indentaion to the template class
template.indentation = indentationIdx

for var in variablesMatch:
    #add detected variables to the tempalte. The Template class handles converting to upper case and parsing different dimensions and keywords
    template.addVariable(var)
#template.printTemplate()
#comment out all declared variables, to add only comment lines and save any resulting asm difference
template.commentToggleTemplate()

with open(filepath,'w') as file:
    print(f"Writing commented out template to: {filepath}")
    #Remove previous dimension declaration
    writeString = fileString[:dimensionLine.start(0)] + fileString[dimensionLine.end(1):]
    writeString = fileString[:implicitStartIdx] + template.getTemplate() + fileString[implicitEdnIdx:]
    file.write(writeString)
print(f"Closed {filepath}")
#Should do a dumpOfiles here and check for assembly difference
#%% Switch Implicit double statement to Implicit none and uncomment template
template.switchImplicitStatement()
#Uncomment the declaretion lines
template.commentToggleTemplate()
with open(filepath,'w') as file:
    print(f"Switching to Implicit none and uncommenting template of: {filepath}")
    #Remove previous dimension declaration
    writeString = fileString[:dimensionLine.start(0)] + fileString[dimensionLine.end(1):]
    writeString = writeString[:implicitStartIdx] + template.getTemplate() + writeString[implicitEdnIdx:]
    file.write(writeString)
print(f"Closed {filepath}")
