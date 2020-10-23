class TypeTemplate:
    recognizedVariables = []
    intIndex = 1
    realIndex = 2
    charIndex = 3
    template = [ [False,'!IMPLICIT NONE'], [False,'!INTEGER(4) ::'], [False,'!REAL(8) ::'], [False,'!CHARACTER() ::'] ]
    indentation = 0
    #Lines template
    def __commentToggle(self, idx):
        """Toggle if the line at template[idx] is commented out or not"""
        if( self.template[idx][1][0] != "!"):
            self.template[idx][1] ="!" + self.template[idx][1]
        else:
            #exclude first comment character, replacing replaces all '!' which can be used for logical expressions
            self.template[idx][1] = self.template[idx][1][1:]

    def addVariable(self, varName):
        """Add a variable to the template list. Case insensitive. Variables are parsed to the proper variable type line by the determineType(varName) method
        name --> variable
        name(dim1,dim2..) --> array """
        varName = varName.upper()
        if("(" and ")" not in varName):
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
        elif("(" and ")" in varName):
            #name = varName[:varName.index("(")]
            #dimension = varName[varName.index("(") : varName.index(")")]
            #addDimension(dimension)
            self.recognizedVariables.append(varName)
            self.addArray(varName)
        else:
            raise SyntaxError(f"Could not identify type of {varName}. If an array make sure to include the dimension in brackets 'name(dim1,dim2,...)'")


    def removeVariable(self, varName):
        """Removes the given variable from the template and the list of recognizedVariables. Case insensitive"""
        varName = varName.upper()
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
            self.template[typeIndex].remove(varName)
            self.removeArray(varName)
        else:
            raise SyntaxError(f"Could not identify type of {varName}. If an array make sure to include the dimension in brackets 'name(dim1,dim2,...)'")



    def determineType(self, varName):
        """Deterines the index in the template list for the given variable.
        0 - implicit none declaration
        1 - INTEGER(4)
        2 - REAL(8)
        3 - CHARACTER(..)
        n - others are detected Dimensions """
        #DetermineType
        varName = str(varName).upper()
        if(ord('I')<= ord(varName[0]) <=ord('N')):
            #INTEGER
            return self.intIndex
        else:
            #REAL(8)
            return self.realIndex
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

    def printTemplate(self):
        """Prints the lines for type declaration. """
        print(self.getTemplate())

    #ADD :: def toggle IMPLICIT NONE
    #TODO :: ADD option to add indentation to declaration - the same for each line
        #for line in self.template:
            #line = [False, '!INTEGER(4) ::', 'var1',...,'varN'] etc
    #
    def addArray(self, arrayName):
        arrayName = arrayName.upper()
        name = arrayName[:arrayName.index("(")]
        dimension = arrayName[arrayName.index("(") : arrayName.index(")")+1]
        typeStr = ''
        dimensionStr = f'DIMENSION{dimension}'
        arrayExists = False
        if(self.determineType(name) == 1):
            typeStr = 'INTEGER(4),'
        elif(self.determineType(name) == 2):
            typeStr = 'REAL(8),'
        else:
            raise TypeError(f"Unknown type for array {arrayName}")

        for idx, line in enumerate(self.template):
            #go through lines to check if dimension was declared
            if(typeStr and dimensionStr in line[1]):
                #Dimension declaration exists, append the name to the line
                ## Add variable names to the dimension declaration TYPE,DIMENSION(I,J) :: array1, array2
                self.template[idx].append(name)
                arrayExists = True
        if(not arrayExists):
            self.template.append([True,f"{typeStr}{dimensionStr} ::",name])

    def removeArray(self, arrayName):
        arrayName = arrayName.upper()
        name = arrayName[:arrayName.index("(")]
        dimension = arrayName[arrayName.index("(") : arrayName.index(")")+1]
        typeStr = ''
        dimensionStr = f'DIMENSION{dimension}'
        arrayRemoved = False
        if(self.determineType(name) == 1):
            typeStr = 'INTEGER(4),'
        elif(self.determineType(name) == 2):
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
##tst.commentToggle(1)
#tst.addVariable("KmaxARRAY(KMAX,JMAX)")
#tst.removeVariable("imaxARRAY(IMAX,JMAX)")
#print(tst.getTemplate())

#%%#####
