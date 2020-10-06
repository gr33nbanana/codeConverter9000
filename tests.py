# %% Importing libraries
from docopt import docopt
import subprocess as sp
from glob import glob
import os
import pathlib
import shutil
import multiprocessing as mp
# %%  runnin parallel
listOfNames = ['name1','name2','name3','name4','name5','name6']
def runThisFun(givenName, someParam = 'hardcoded'):
    print(f"given name: {givenName}")
    print(f"some parameter: {someParam} ")

pool = mp.Pool(mp.cpu_count(), maxtasksperchild = 2)
pool.map_async(runThisFun, listOfNames)
pool.close()
pool.join()
