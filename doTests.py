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

regex = r".*?DO.*?(\d+)[\s\S]*?(?=\n\d+)"
matches = re.finditer(regex, test_str, re.MULTILINE | re.IGNORECASE)


doidx = []
for matchNum, match in enumerate(matches):
	print(f"matchNum: {matchNum}")
	doidx.append(match.end())
doidx
#doidx
flag = "HERE\n"
displace = len(flag)

accumulator = 0
for idx in doidx:
	#0...n
	removed = test_str[idx + 1 + accumulator:].find('\n')+1
	test_str = test_str[:idx + 1 + accumulator] + flag + test_str[idx + 1 + accumulator + removed:]
	accumulator += displace - removed
	#

print(test_str)

#
