class TypeTemplate:
    recognizedVariables = []
    intIndex = 1
    realIndex = 2
    charIndex = 3
    template = [ ['IMPLICIT NONE'], [False,'!INTEGER(4) ::'], [False,'!REAL(8) ::'], [False,'!CHARACTER()'] ]
    #Lines template

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
            self.template[typeIndex][1] = self.template[typeIndex][1].replace("!","")

    def removeVariable(self, varName):
        #Remove variable:
        ##--if it's the last variable, set flag to False
        varName = varName.upper()
        typeIndex = self.determineType(varName)
        self.template[typeIndex].remove(varName)
        if( len( self.template[typeIndex] ) == 2 ):
            self.template[typeIndex][0] = False
            self.template[typeIndex][1] ="!"+self.template[typeIndex][1]

    def determineType(self, varName):
        #DetermineType
        varName = str(varName).upper()
        if(ord('I')<= ord(varName[0]) <=ord('N')):
            #INTEGER
            return self.intIndex
        else:
            return self.realIndex
#%%##############################################################
tst = TypeTemplate()
tst.template
tst.addVariable("amax")
tst.removeVariable("amax")


######
ord('I')<= ord('') <=ord('N')

a = [ [False,'!INTEGER(4) ::'] ]
idx = 0

a[idx][1].replace("!","")
a[idx][1]
len(a[idx])
a[idx].append("IMAX")
a[idx].index("IMAX")
a[idx].remove("ZMAX")
', '.join( a[idx][2:] )

a[1][0] = "!"+a[1][0]
