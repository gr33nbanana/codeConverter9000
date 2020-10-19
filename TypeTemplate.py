class TypeTemplate:
    recognizedVariables = []
    intIndex = 1
    realIndex = 2
    charIndex = 3
    template = [ [False,'!IMPLICIT NONE'], [False,'!INTEGER(4) ::'], [False,'!REAL(8) ::'], [False,'!CHARACTER() ::'] ]
    #Lines template
    def __commentToggle(self, idx):
        if( self.template[idx][1][0] != "!"):
            self.template[idx][1] ="!" + self.template[idx][1]
        else:
            self.template[idx][1] = self.template[idx][1].replace("!","")

    def addVariable(self, varName):
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
        #DetermineType
        varName = str(varName).upper()
        if(ord('I')<= ord(varName[0]) <=ord('N')):
            #INTEGER
            return self.intIndex
        else:
            #REAL(8)
            return self.realIndex
    def getTemplate(self):
        declarationLines = []
        for line in self.template:
            declarationLines.append( line[1] + ", ".join( line[2:] ) )
        return declarationLines

    def printTemplate(self):
        for line in self.getTemplate():
            print(line)
#%%##############################################################
tst = TypeTemplate()
tst.template
#tst.commentToggle(1)
tst.addVariable("zMax")
tst.removeVariable("zmax")
tst.printTemplate()

#%%#####




















##
