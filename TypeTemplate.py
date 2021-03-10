import warnings

class TypeTemplate:
    def __init__(self):
        self.recognizedVariables = []
        self.implicitDoubleIndex = 0
        self.implicitNoneIndex = 1
        self.intIndex = 2
        self.realIndex = 3
        self.charIndex = 4
        self.template = [[False, 'IMPLICIT DOUBLE PRECISION (A-H,O-Z)'], [False,'!IMPLICIT NONE'], [False,'!INTEGER(4) ::'], [False,'!REAL(8) ::'], [False,'!CHARACTER() ::'] ]
        self.indentation = 0

    #Lines template
    def __commentToggle(self, idx):
        """Toggle if the line at template[idx] is commented out or not"""
        if( self.template[idx][1][0] != "!"):
            self.template[idx][1] ="!" + self.template[idx][1]
        else:
            #exclude first comment character
            #All commenting should be handled by the function so it should always be the first character
            self.template[idx][1] = self.template[idx][1][1:]

    def commentToggleTemplate(self):
        """Comment or Uncomment the lines of the template with declared variables.
        Empty decleration lines are commented out by default. """
        for idx, line in enumerate(self.template):
            if(line[0]):
                self.__commentToggle(idx)

    def _commentOutIndex(self, idx):
        """
        Add a comment symbol '!' to the index line if there is not one
        """
        if( self.template[idx][1][0] != "!"):
            self.template[idx][1] ="!" + self.template[idx][1]
        else:
            pass

    def _uncommentIndex(self, idx):
        """
        Remove comment symbol '!' frp, index line if there is one
        """
        if( self.template[idx][1][0] == "!"):
            self.template[idx][1] = self.template[idx][1][1:]
        else:
            pass

    def commentAllTemplate(self):
        """
        Comment out all uncommented declerations with variables
        """
        for idx, line in enumerate(self.template):
            if(line[0]):
                #IF TRUE flag is set then there are variables
                print(f"DEBUGING: idx = {idx}")
                self._commentOutIndex(idx)

    def uncommentAllTemplate(self):
        """
        Uncomment all commented out declarations with variables
        """
        for idx, line in enumerate(self.template):
            if(line[0]):
                self._uncommentIndex(idx)

    def switchImplicitStatement(self):
        self.__commentToggle(self.implicitDoubleIndex)
        self.__commentToggle(self.implicitNoneIndex)

    def addVariable(self, varName):
        """Add a variable to the template list. Case insensitive. Variables are parsed to the proper variable type line by the determineType(varName) method
        name --> variable
        name(dim1,dim2..) --> array """
        print(f"DEBUGING: variable passed to addVariable: {varName}")
        varName = varName.upper()
        if(varName not in self.recognizedVariables):
            if("(" not in varName and ")" not in varName):
                #Add variable:
                ##--Add to list of all variables
                self.recognizedVariables.append(varName)
                ##--if first, uncomment or add '!' when concatinatig dep on flag value)
                ##--only add as new element to list
                typeIndex = self.determineType(varName)
                self.template[typeIndex].append(varName)
                if(self.template[typeIndex][0] == False):
                    self.template[typeIndex][0] = True
                    self.__commentToggle(typeIndex)
                    #self.template[typeIndex][1] = self.template[typeIndex][1].replace("!","")
            elif("(" in varName and ")" in varName):
                #name = varName[:varName.index("(")]
                #dimension = varName[varName.index("(") : varName.index(")")]
                #addDimension(dimension)
                self.recognizedVariables.append(varName)
                self.__addArray(varName)
            else:
                raise SyntaxError(f"Could not identify type of {varName}. If an array make sure to include the dimension in brackets 'name(dim1,dim2,...)'")
        else:
            warnings.warn(f"Warning variable {varName} already declared, cannot add to template")

    def removeVariable(self, varName):
        """Removes the given variable from the template and the list of recognizedVariables. Case insensitive"""
        varName = varName.upper()
        if(varName in self.recognizedVariables):
            self.recognizedVariables.remove(varName)
            if("(" and ")" not in varName):
                #Remove variable:
                ##--if it's the last variable, set flag to False
                typeIndex = self.determineType(varName)
                self.template[typeIndex].remove(varName)
                if( len( self.template[typeIndex] ) == 2 ):
                    self.template[typeIndex][0] = False
                    self.__commentToggle(typeIndex)
                    #self.template[typeIndex][1] ="!"+self.template[typeIndex][1]
            elif("(" and ")" in varName):
                self.__removeArray(varName)
            else:
                raise SyntaxError(f"Could not identify type of {varName}. If an array make sure to include the dimension in brackets 'name(dim1,dim2,...)'")
        else:
            warnings.warn(f"Warning variable {varName} is not present in the template. Cannot remove from template.")
#
    def determineType(self, varName):
        """Deterines the index in the template list for the given variable.
        0 - implicit double declaration
        1 - implicit none declaration
        2 - INTEGER(4)
        3 - REAL(8)
        4 - CHARACTER(..)
        n - others are detected Dimensions """
        #DetermineType
        varName = str(varName).upper()
        if(ord('I')<= ord(varName[0]) <=ord('N')):
            #INTEGER
            return self.intIndex
        else:
            #REAL(8)
            return self.realIndex
        #TODO :: Add handling of Character type
    def getTemplate(self):
        """Returns a string contianing the lines for type declaration
        """
        declarationLines = []
        for line in self.template:
            declarationLines.append( " "*self.indentation + line[1] + ", ".join( line[2:] ) )
        declarationString = ""
        for line in declarationLines:
            declarationString += line + "\n"
        return declarationString
        # One line 109-112 : return "\n".join(declarationLines) + "\n"

    def printTemplate(self):
        """Prints the lines for type declaration. """
        print(self.getTemplate())
    #
    def __addArray(self, arrayName):
        arrayName = arrayName.upper()
        name = arrayName[:arrayName.index("(")]
        dimension = arrayName[arrayName.index("(") : arrayName.rfind(")")+1]
        dimensionStr = f'DIMENSION{dimension}'
        arrayExists = False
        if(self.determineType(name) == self.intIndex):
            typeStr = 'INTEGER(4),'
        elif(self.determineType(name) == self.realIndex):
            typeStr = 'REAL(8),'
        else:
            raise TypeError(f"Unknown type for array {arrayName}")
        for idx, line in enumerate(self.template):
            #go through lines to check if dimension was declared
            if(typeStr in line[1] and dimensionStr in line[1]):
                #Dimension declaration exists, append the name to the line
                ## Add variable names to the dimension declaration TYPE,DIMENSION(I,J) :: array1, array2
                self.template[idx].append(name)
                arrayExists = True
        if(not arrayExists):
            self.template.append([True,f"{typeStr}{dimensionStr} ::",name])

    def __removeArray(self, arrayName):
        arrayName = arrayName.upper()
        name = arrayName[:arrayName.index("(")]
        dimension = arrayName[arrayName.index("(") : arrayName.rfind(")")+1]
        typeStr = ''
        dimensionStr = f'DIMENSION{dimension}'
        arrayRemoved = False
        if(self.determineType(name) == self.intIndex):
            typeStr = 'INTEGER(4),'
        elif(self.determineType(name) == self.realIndex):
            typeStr = 'REAL(8),'
        else:
            raise TypeError(f"Unknown type for array {arrayName}")

        for idx, line in enumerate(self.template):
            #Check if line[1] contains all the required keywords: Type, dimension etc
            if(typeStr and dimensionStr in line[1]):
                self.template[idx].remove(name)
                arrayRemoved = True
                if(len(self.template[idx]) <= 2):
                    #If the dimension declaration is empty "[True,'TYPE(),DIMENSION(I,J) ::']"
                    self.template.remove(self.template[idx])

        if(not arrayRemoved):
            raise AssertionError(f"Array {arrayName} not found in template")

#%%##############################################################
#tst = TypeTemplate()
#tst.template
#tst.recognizedVariables
#tst.addVariable("IMAX2")
#tst.commentToggleTemplate()
#tst.commentAllTemplate()
#tst.uncommentAllTemplate()
#tst.switchImplicitStatement()
#tst.removeVariable("IMAX(DIM1,DIM2)")
#print(tst.getTemplate())








#%%#####
