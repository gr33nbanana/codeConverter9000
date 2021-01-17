import re
test_str = ("   DO 50 I=2,ITOT\n"
	"      NON0(I) = NON0(I)+NON0(I-1)\n"
	"50 KD(I)   = KD(I)+NON0(I-1)\n\n"
	"10 KT   = 0\n"
	"   MSUB = 0\n"
	"   FLXB = 0.0\n"
	"   PWR  = 0.0\n"
	"   BURN = 0.0\n"
	"   DO 20 J=1,ITMAX\n"
	"      XZH(J)   = 0.0\n"
	"      XZHOM(J) = 0.0\n"
	"20 XHOM(J)  = 0.0\n"
	"   DO 30 J=1,10\n"
	"30 POWER(J) = 0.0\n"
	"40 LRETU=.FALSE.\n\n"
	"   DO 20 J=1,ITMAX\n"
	"      XZH(J)   = 0.0\n"
	"      XZHOM(J) = 0.0\n"
	"20 XHOM(J)  = 0.0\n\n"
	"   DO 72 J=1,63\n"
	"72 NTO(J) = 1\n")

regex = r"(.*)?DO[ ]*?(?=\d+)(\d+)[\s\S]*?(?=\n(\d+))"
matches = re.finditer(regex, test_str, re.MULTILINE | re.IGNORECASE)

doidx = []
for matchNum, match in enumerate(matches):
	print(f"matchNum: {matchNum}")
	#Group 1 -- indentation
	#Group 2 -- first Address of DO LOOP
	#Group 3 -- exit Address of DO LOOP
	indentation = " "*(match.end(1) - match.start(1))
	doidx.append([indentation, [match.start(2),match.end(2)], [match.start(3), match.end(3)]])
doidx
#doidx
flagEND_DO = 'END DO\n'

accumulator = 0
for idxPair in doidx:
	#Replace first Address with whiteSpace
	test_str = test_str[ : idxPair[1][0]] + " "*(idxPair[1][1] - idxPair[1][0]) + test_str[idxPair[1][1] : ]
	#Replace second Address with whiteSpace
	test_str = test_str[ : idxPair[2][0]] + " "*(idxPair[2][1] - idxPair[2][0]) + test_str[idxPair[2][1] : ]
print("TEST STRING AFTER REMOVING DO ADDRESSES:")
print(test_str)

for idxPair in doidx:
	#Line after last Do statement
	newLineIdx = accumulator + idxPair[2][1] + test_str[accumulator + idxPair[2][1]: ].find('\n') + 1
	test_str = test_str[ : newLineIdx] + idxPair[0] + flagEND_DO + test_str[newLineIdx : ]
	accumulator += len(idxPair[0]) + len(flagEND_DO)
print("TEST STRING AFTER ADDING END DO STATEMENT:")
print(test_str)

#
