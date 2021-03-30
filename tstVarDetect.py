import subprocess as sp
compileArgs = "cd _build && make"
detectedVariables = []
proc = sp.Popen(compileArgs, shell = True, stdout = sp.PIPE, stderr = sp.STDOUT)
for line in proc.stdout.readlines():
    line = line.decode("utf-8")
    if("‘" and "’" in line):
        variableName = line[line.index("‘")+1 : line.index("’")]
        detectedVariables.append(variableName)

print("DETECTED VARIABELS:\n",detectedVariables)
