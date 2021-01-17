import fnmatch
import warnings
from docopt import docopt
from glob import glob
import re
import TypeTemplate as tmp
import subprocess as sp
from pathlib import Path

#TODO :: add docopt documentation
args = docopt(__doc__, version = '1.0')

regex = r"(.*)?DO[ ]*?(?=\d+)(\d+)[\s\S]*?(?=\n(\d+))"


#Main loop
#For every file:
#test_str is the file_string
matches = re.finditer(regex, test_str, re.MULTILINE | re.IGNORECASE)

doidx = []

for matchNum, match in enumerate(matches):
	#Get positions of all old DO statements
	print(f"matchNum: {matchNum}")
	#Group 1 -- indentation
	#Group 2 -- first Address of DO LOOP
	#Group 3 -- exit Address of DO LOOP
	indentation = " "*(match.end(1) - match.start(1))
	doidx.append([indentation, [match.start(2),match.end(2)], [match.start(3), match.end(3)]])
#TODO :: Add END DO line as a comment (don't Change anything else)
#TODO :: compile and commit any assembly changes with message "changes from comments"


flagEND_DO = 'END DO\n'
accumulator = 0
for idxPair in doidx:
	#Replace first Address with whiteSpace
	test_str = test_str[ : idxPair[1][0]] + " "*(idxPair[1][1] - idxPair[1][0]) + test_str[idxPair[1][1] : ]
	#Replace second Address with whiteSpace
	test_str = test_str[ : idxPair[2][0]] + " "*(idxPair[2][1] - idxPair[2][0]) + test_str[idxPair[2][1] : ]
#print("TEST STRING AFTER REMOVING DO ADDRESSES:")
#print(test_str)

for idxPair in doidx:
	#Line after last Do statement
	newLineIdx = accumulator + idxPair[2][1] + test_str[accumulator + idxPair[2][1]: ].find('\n') + 1
	test_str = test_str[ : newLineIdx] + idxPair[0] + flagEND_DO + test_str[newLineIdx : ]
	accumulator += len(idxPair[0]) + len(flagEND_DO)
#print("TEST STRING AFTER ADDING END DO STATEMENT:")
#print(test_str)

#TODO :: add git commit -- this is after DO loop has been changed
