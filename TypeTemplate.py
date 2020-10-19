class TypeTemplate:
    recognizedVariables = []
    intIndex = 1
    realIndex = 2
    charIndex = 3
    template = [ [False,'!IMPLICIT NONE'], [False,'!INTEGER(4) ::'], [False,'!REAL(8) ::'], [False,'!CHARACTER() ::'] ]
    #Lines template
    def __commentToggle(self, idx):
        """Toggle if the line at template[idx] is commented out or not"""
        if( self.template[idx][1][0] != "!"):
            self.template[idx][1] ="!" + self.template[idx][1]
        else:
            self.template[idx][1] = self.template[idx][1].replace("!","")

    def addVariable(self, varName):
        """Add a variable to the template list. Case insensitive. Variables are parsed to the proper variable type line by the determineType(varName) method """
        varName = varName.upper()
        #Add variable:
        ##--Add to list of all variables
        self.recognizedVariables.append(varName)
        ##--if first, uncomment (or add '!' when concatinatig dep on flag value)
        ##--only add as new element to list
        ##--getTemplate concatinates all the elements on 1 string
        typeIndex = self.determineType(varName)
        self.template[typeIndex].append(varName)
        if(self.template[typeIndex][0] == False):
            self.template[typeIndex][0] = True
            self.__commentToggle(typeIndex)
            #self.template[typeIndex][1] = self.template[typeIndex][1].replace("!","")

    def removeVariable(self, varName):
        """Removes the given variable from the template and the list of recognizedVariables. Case insensitive"""
        #Remove variable:
        ##--if it's the last variable, set flag to False
        varName = varName.upper()
        typeIndex = self.determineType(varName)
        self.template[typeIndex].remove(varName)
        if( len( self.template[typeIndex] ) == 2 ):
            self.template[typeIndex][0] = False
            self.__commentToggle(typeIndex)
            #self.template[typeIndex][1] ="!"+self.template[typeIndex][1]

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
        """Returns a list of strings contianing the lines for type declaration
        ['IMPLICIT NONE', 'INTEGER(4) :: var1,var2', ...]"""
        declarationLines = []
        for line in self.template:
            declarationLines.append( line[1] + ", ".join( line[2:] ) )
        return declarationLines

    def printTemplate(self):
        """Prints the lines for type declaration. """
        for line in self.getTemplate():
            print(line)

    ## TODO: DIMENSION PARSER
    #
#%%##############################################################
tst = TypeTemplate()
tst.template
#tst.commentToggle(1)
tst.addVariable("kmax")
tst.removeVariable("kmax")
tst.printTemplate()

#%%#####




















##
