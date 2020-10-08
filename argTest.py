"""argTest.py
Usage:
  argTest.py what [--only=<filename>... --changeArg]
  argTest.py parallel

Options:
  --only <name1,name2>    Only convert these files. Was their parsing specified here?
  --changeArg             Can you change an arg value? [default: True]
"""

from docopt import docopt
import subprocess as sp
args = docopt(__doc__, version = '1.0')
if(args['what']):
    print(args['--only'])
    print("Value of --changeArg: ", args['--changeArg'])

    if(args['--changeArg']):
        args['--only'] = ['CHANGED ARGS! SUCCESS!']
        print("New --only args: ", args['--only'])
    def testFun():
        """Does this string interfere with docopt?"""

from functools import partial
import multiprocessing as mp

def myFun(fileName, loc="PATH/TOFILE", ext = ""):
    print(f"{loc}{fileName}{ext}")

if __name__ == "__main__":
    iterable = ["filename","filename2","filename3","filename4","filename","filename2","filename3","filename4","filename","filename2","filename3","filename4","filename","filename2","filename3","filename4","filename","filename2","filename3","filename4"]
    givenExt = ".ssd"
    func = partial(myFun, ext=".f9000")
    pool = mp.Pool()
    pool.map_async(func,iterable)
    pool.close()
    pool.join()
