import re

ifParser = re.compile(r"(IF\s*?\(.*?\))\s*?(\d+),(\d+),(\d+)  ", re.IGNORECASE | re.VERBOSE | re.DOTALL)

filePath = "./testIFS.txt"

with open(filePath, 'r') as file:
    fileString = file.read()

matches = ifParser.finditer(fileString)
ifList = []
def ifWriter(indent: int, statement: str, value1: str, value2: str, value3: str) -> str:
    returnStr = ''
    #if v1 == v2  IF (A <= 0)
    #group(1)[:-1] + '<= 0)'
    #elif V2 == v3 IF (a <  0)
    #else IF(a <0) IF (a == 0) if (a > 0)
    if(value1 == value2):
        #Less or equal to 0
        statement = statement[:-1] + ' <= 0) THEN\n'

        returnStr = " "*indent + f"{statement}" + " "*(indent + 2) + f"GOTO {value1}\n" + " "*indent + "ELSE\n" + " "*(indent + 2) + f"GOTO {value3}\n"+ " "*indent +"END IF\n"
    elif(value2 == value3):
        statement = statement[:-1] + ' < 0) THEN\n'

        returnStr = " "*indent + f"{statement}" + " "*(indent + 2) + f"GOTO {value1}\n" + " "*indent + "ELSE\n" + " "*(indent + 2) + f"GOTO {value3}\n"+ " "*indent +"END IF\n"
    else:
        statement1 = statement[:-1] + ' < 0) THEN\n'
        statement2 = statement[:-1] + ' == 0) THEN\n'

        returnStr = " "*indent + f"{statement1}" + " "*(indent + 2) + f"GOTO {value1}\n" + " "*indent + f"ELSE {statement2}" + " "*(indent + 2) + f"GOTO {value2}\n" + " "*indent +"ELSE\n" + " "*(indent + 2) + f"GOTO {value3}\n" + " "*indent + "END IF\n"
    return returnStr

for matchNum , match in enumerate(matches):
    indent = match.start(1) - fileString[:match.start(1)].rfind("\n") - 1

    ifStatementString = ifWriter(indent, match.group(1), match.group(2), match.group(3), match.group(4))

    ifList.append([match.start(0),match.end(4), ifStatementString])

ifList
accumulator = 0
writeString = fileString
for statement in ifList:
    with open(filePath, 'w') as file:
        writeString = writeString[:statement[0] + accumulator] + statement[2] + writeString[statement[1] + accumulator:]
        file.write(writeString)
    accumulator += len(statement[2]) - (statement[1] - statement[0])

for st in ifList:
    print(st[2])
