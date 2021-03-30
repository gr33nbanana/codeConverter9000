#%% First test cell
import re
test_str = ("BLABLA\n"
	"BLABLA\n\n\n"
	"   DIMENSION ABTEM(IMAX,JMAX),DZCORE(NLPLD:JMAX),&\n"
	"   &          KZRAB(IMAX,JMAX)\n"
	"   PARAMETER (DHFEP = 268.0D3) ! latent melt enthalpy of iron\n"
	"   PARAMETER (zero  = 0.0D0)")

regex = r"^(?!.*?\!)\s*?DIMENSION(?=((.*\&\s*\n\s*\&)*.*\n?))(?!.+(\s+\:))"
matches = re.finditer(regex, test_str, re.MULTILINE | re.IGNORECASE)
print(f"INTIAL:\n{test_str}")
for matchNum, match in enumerate(matches):
	idxList = []
	dimString = test_str[:match.start(1)]
	commentDim = dimString.rfind('\n') + 1
	print("DIMESNION STRING: ", dimString)
	print("INDEX NEWLINE: ", commentDim)
	idxList.append(commentDim)
	for idx, letter in enumerate(match.group(1)[:-1]):
		if(letter == '\n'):
			idxList.append( match.start(1) + idx + 1)
accumulator = 0
for idx in idxList:
	test_str = test_str[:idx + accumulator] + "!" + test_str[idx + accumulator:]
	accumulator += len("!")

print("FINAL:\n",test_str)
#########
#%% Second test cell
import fnmatch
some_paths = ['paht/to/file.cpp', 'path/to/.folder', 'path/to/file.F90']
ignore_information = ['*.cpp*', '*.folder*']

some_paths = [n for n in some_paths if not any(fnmatch.fnmatch(n, ignore) for ignore in ignore_information)]
some_paths

#%%
# Can I just get a list of indencies of the match group ?
# or return -> [indentation, [match.start, match.end], [match.start, match.end]]
# Then responsibility is when calling in the __main__ to know the correct amount of groups for the given regex
################ Variations of the replacement ########################
#######################################################################
doidx.append([indentation, [match.start(2),match.end(2)], [labelStart, labelEnd]])
commented_string = test_str
comment_accumulator = 0
commentFlagEND_DO = "!END DO\n"
#TODO :: make into a function: for idxPair in doidx:
#       writeDostatement / writeStatement("DO" / function?, doidx)
#      -- could be used in other scripts like adding type template, arithmetic IF

for idxPair in doidx:
	#idxPair has indentation and index of first label at DO statement end second label where do GOES TO
	#idxPair = [" indentaion", [indexSTART,indexEND], [indexSTART, indexEND]]
    lineStartOfIndex = comment_accumulator + idxPair[2][1]
	commentNewLineIdx = lineStartOfIndex + commented_string[lineStartOfIndex + idxPair[2][1] : ].find('\n') + 1

	commented_string = commented_string[ : commentNewLineIdx] + commentFlagEND_DO + commented_string[commentNewLineIdx : ]

	comment_accumulator += len(commentFlagEND_DO)
###################### return new string #########################
##################################################################
###########################################################
#Write END DO statement in the file
flagEND_DO = 'END DO\n'
accumulator = 0
#################################
########### DO NOT CONSIDER #####
########## FUNCTION ALREADY EXISTS insertInString(index1,index2 etc)
#for idxPair in doidx:
	##Replace first Address with whiteSpace
	##########################################
	## Adds a string between given index,  || Given string \/ ||
	#test_str = test_str[ : idxPair[1][0]] + " "*(idxPair[1][1] - idxPair[1][0]) + #test_str[idxPair[1][1] : ]
	##Replace second Address with whiteSpace
	##test_str = test_str[ : idxPair[2][0]] + " "*(idxPair[2][1] - idxPair[2][0]) + #test_str[idxPair[2][1] : ]
############################################
for idxPair in doidx:
	#Line after last Do statement
	lineStartOfIndex = accumulator + idxPair[2][1]
	newLineIdx = lineStartOfIndex + test_str[lineStartOfIndex: ].find('\n') + 1
	### insertInString(index, index, idxPair[0] + flagEND_DO )
	test_str = test_str[ : newLineIdx] + idxPair[0] + flagEND_DO + test_str[newLineIdx : ]
	accumulator += len(idxPair[0]) + len(flagEND_DO)


# %% Testing recursion

def recFun(int1, int2, someList):
	if(int2 > 0):
		someList.append(int1)
		recFun(int1, int2 - 1, someList)
	return
lstA = []
lstA

recFun(5, 5, lstA)

# %%
import re

regex = r"^(?!\!)(.*)?DO[ ]*?(?=\d+)(\d+)[\s\S]*?(?=\n(\s*?\2[\D]+?))"

test_str = ("DO 100\n"
	"  CODE\n"
	"  CODE\n"
	"  DO 200\n"
	"    CODE\n"
	"200 CODE\n"
	"  CODE\n"
	"  DO 300\n"
	"    CODE\n"
	"    DO 400\n"
	"      CODE\n"
	"400 CONTINUE\n"
	"300 CODE\n"
	"100 CODE\n")

matches = re.finditer(regex, test_str, re.MULTILINE)


print("=============================================")
for matchNum, match in enumerate(matches, start=1):

    print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group(0)))

    for groupNum in range(0, len(match.groups())):
        groupNum = groupNum + 1

        print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

#%% ####################################
testinglst = []


test_str = ("DO 100\n"
	"  CODE\n"
	"  CODE\n"
	"  DO 200\n"
	"    CODE\n"
	"200 CODE\n"
	"  CODE\n"
	"  DO 300\n"
	"    CODE\n"
	"    DO 400\n"
	"      CODE\n"
	"400 CONTINUE\n"
	"300 CODE\n"
	"100 CODE\n")


def getDoRegexIndecies(regex, givenString, storingList, globalIdx = 0):
    """
    Appends indecies of all the starting positions of matches for the given regex in the given string
    to the provided list reference.
    Parameters
    ----------
        regex : SRE_Pattern
            regular experssion which is used to parse the given string
        givenString : str
            string on which the regular expression will be used
        storingList : list
            List of found indecies

    Returns
    -------
        list : int
            Returns a list containing the string indecies of found matches from the given regex in the given string.
    """
    match = re.search(regex, givenString, re.MULTILINE | re.IGNORECASE)
    if( type(match) == type(None) ):
        #if not found return
        return
    indentation = " "*(match.end(1) - match.start(1))
    match2GlobalStart = globalIdx + match.start(2)
    match2GlobalEnd   = globalIdx + match.end(2)
    match3GlobalStart = globalIdx + match.start(3)
    match3GlobalEnd   = globalIdx + match.end(3)

    storingList.append( [indentation, [match2GlobalStart, match2GlobalEnd],[match3GlobalStart, match3GlobalEnd]])
    #then run the same on the rest of the string and the matched strigns to check for sub occurance until nothing is found
    # Give some Reference Index ?? to add to the match group indecies
    # fun( globalIdx = 0):
    #   fun( globalIdx = globalIdx + something)
    # -----> fun(globalIdx = (globalIdx something) + somethingElse)

    #The concatination of " " is needed to properly recognize a match group if it's exactly in the end
    getDoRegexIndecies(regex, match.group(0) +" ", storingList, globalIdx = globalIdx + match.start(0))

    getDoRegexIndecies(regex, givenString[match.end(3):], storingList, globalIdx = match3GlobalEnd)
    # Containing string is in match.group() or match.group(0)
    # BUT how do you keep the correct indeceis? --> append match.start + getIndex(matchString)


getDoRegexIndecies(regex, test_str, testinglst)
testinglst



#%% Testing return code

import subprocess as sp
def checkComplete(makeCommand):
	proc = sp.Popen(makeCommand, shell=True, stdout = sp.PIPE, stderr=sp.STDOUT)
	returnCode = proc.wait()
	print(f"returned code: {returnCode}")

checkComplete("dirrr")
