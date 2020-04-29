"""argTest.py
Usage:
  argTest.py what [--only=<filename>...]

Options:
  --only <name1,name2>    Only convert these files. Was their parsing specified here?
"""

from docopt import docopt

args = docopt(__doc__, version = '1.0')
print(args['--only'])
print(args['--only'][0].split(' '))
print(args['--only'][0].split(' ')[0])
print(args['--only'][0].split(' ')[1])
