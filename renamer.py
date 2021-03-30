from glob import glob
import subprocess as sp
def collectPaths(fromType):
    """Returns a list of all files in the specified --path with the specified extension <fromtype>
    """
    paths = glob(f"**/*{fromType}", recursive = True)
    return paths

def renameAndClean():
    print("Running renameAndClean")
    """Runs collectPaths() for '_.f90' helper files and renames the corresponding '.f' files to have the proper '.f90' extension.
    If '--clean' option is given it will delete the '_.f90' helper files
    Only renames 30 files then prompts a user key stroke. Pausing is inteded to check if GitKraken or other Version Control has correctly detected a rename."""
    paths = collectPaths(fromType = '.f90')
    maxCount = 30
    for pathName in paths:
        if(maxCount <= 0):
            maxCount = 30
            #GitKraken cannot process more than 60-120 files at a time, before the changes stop being recognized as rename and become delte + create, loosing the commit history
            input("Renaming paused. Check if Version control can handle the amount of renamed files.\nPress any key to continue")
        maxCount -= 1
        oldPath = pathName
        outputPath = oldPath[:-3] + "F90"
        try:
            shellArg = f"git mv {oldPath} {outputPath}"
            sp.call(shellArg, shell=True)
            print(shellArg)
        except:
            print(f"Could not execute {shellArg}")
            continue
if __name__=='__main__':
    renameAndClean()
