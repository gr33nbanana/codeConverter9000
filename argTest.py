"""argTest.py
Usage:
  argTest.py what [--only=<filename>... --changeArg]

Options:
  --only <name1,name2>    Only convert these files. Was their parsing specified here?
  --changeArg             Can you change an arg value? [default: True]
"""

from docopt import docopt
import subprocess as sp
args = docopt(__doc__, version = '1.0')
print(args['--only'])
print("Value of --changeArg: ", args['--changeArg'])

if(args['--changeArg']):
    args['--only'] = ['CHANGED ARGS! SUCCESS!']
    print("New --only args: ", args['--only'])
