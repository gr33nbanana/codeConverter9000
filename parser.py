import re
import TypeTemplate as tmp

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
template.indentation = indentationIdx

for var in variablesMatch:
    #add detected variables to the tempalte. The Template class handles converting to upper case and parsing different dimensions and keywords
    template.addVariable(var)

with open(filepath,'w') as file:
    print(f"Opening to write: {filepath}")
    #Remove previous dimension declaration
    fileString = fileString[:dimensionLine.start(0)] + fileString[dimensionLine.end(1):]
    writeString = fileString[:implicitStartIdx] + template.getTemplate() + fileString[implicitEdnIdx:]
    file.write(writeString)
print(f"Closed {filepath}")
