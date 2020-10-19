import re

#Can replace DIMENSION with any keyword
dimensionPattern = r"DIMENSION(?=((.*\&\n\&)*.*\n?))"

pars_DIMENSION = re.compile(dimensionPattern,flags = re.IGNORECASE)

#findall matches in a string, the variables and any line continuation after the keyword are in the first match
#matches = pars_DIMENSION.findall(text)
#matches[0][0]
