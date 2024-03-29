# Prerequisites
## Ubuntu 20 LTS or Ubuntu 20.04 LTS subsystem for Windows
The code executes bash commands for gathering assembly code and compiling. It can be ran on Ubuntu 20.04 LTS or a Ubuntu subsystem for Windows which is free on the Microsoft [store][1]

## Git 2.17.5 or newer
The script uses [Git][4] for version control, renaming and checking if there are undesired assembly differences.

# Python version and packages
The script was written and tested in python 3.6.9. It is recommended to use the same version.\
The required packages are:
* [docopt][2]
version 0.6.2
* [findent][3] version 2.8.2

# Installation
Clone the repository to a desired directory. When running scripts the directory has to be provided to python3.
# Usage

## CMake or Make
Some scripts require a command to compile the fortran files.\
If you are using CMake to compile your Fortran code, use the option `--withCMake`.\
If you are using Make to compile your Fortran code, use the option `--withMake`

## Folder for assembly code
The script creates a folder named 'DumpedFiles' by default in which it stores the assembly code after compiling. The .asm files are used to check if any undesired difference was introduced when changing the fortran files.\
**NOTE:** **If a different folder name is specified with the terminal options it should be specified for every parser:** typeParser.py, doParser.py, ifParser.py

## Converting fixed-format to free-format
The conversion from fixed to free format is done in two parts.\
First the free-format fortran code is saved in temporary files with  the extension `_.F90` and the contents of the `.f` file is overwritten.\
Then the `.f` file extension is changed to `.F90` and the helper `_.F90` file is removed if the option `--clean` is given.\
After the files are changed and you are using CMake you have to update any dependencies on the file extension before compiling again to overwrite the assembly code and see if there are any undesired differences.


Start by navigating to the root folder which should contain the `.gitignore` file.\
To change the fixed format `.f` syntax to free format run:
```
python3 (path/to/codeConverter9000/)converter9000.py sisyphus .f uphill (--withCMake | --withMake) --recursive
```
**NOTE** Specify only `--withCmake` or `--withMake` depending on which compiler you use.

If no `--dump_at=` is specified and the default assembly dump folder name is not detected, the script will create the folder, compile the program and save the initial assembly code for comparison.

If you want to convert only one folder run:
```
python3 (path/to/codeConverter9000)/converter9000.py sisyphus .f uphill (--withCmake | --withMake) --path=(full/path/to/desired/folder/)
```
**NOTE** You have to add the last backslash in the folder path.

You can also convert only one file in that folder by specifying ```--only=(file_name.f)```

* **Using CMake**\
If you are compiling the fortran files with CMake and you do not have a CMakeLists.txt file in the root directory, after the free formatting you have to manually go to your `CMakeLists.txt` file and update the filenames or paths with the correct new `.F90` extension. If not, the next step will not be able to compile the program and overwrite the assembly code so you would have to do it manually using the `hephaestus --withCMake` command.
* **Using Make**\
If you are compiling the fortran files with make, if you do not specify the `--clean` option, the helper files will not be deleted automatically and they might be compiled as well so you might get some extra assembly files.

## **IMPORTANT:**
* At this stage if the files were formatted correctly, make sure to commit the changed contents of the `.f` files before proceeding. If this is not done Git will not be able to keep the file history after its extension is changed in the next step and will instead show a newly created `.F90` file.\
After comitting stage the created `.asm` assembly files. This way if there are any changes to the assembly files in the end, they will show up as unstaged differences.


Next to change the extension of the `.f` files and delete the `_.F90` helper files run:
```
python3 (path/to/codeConverter9000)/converter9000.py sisyphus .f downhill (--withCMake | --withMake) --clean --recursive
```


## Type declaring undeclared variables

### File format
The script only works on fortran files which contain only one implicit declaration and it is before any dimension declaration.\
**Not supported:**
* `PARAMTER(X)` Some fortran files contain a PARAMETER declaration which is used in arrays. The script does not detect them and will write the detected DIMENSION declaration right after the `IMPLICIT` declaration. You would need to manually move the parameter declaration line to be before the declared dimension for the file to compile afterwards.\
You can either open a new bash terminal or stop the existing script. After you manually change the position of the parameter declaration simply run the hephaestus command to compile and overwrite the assembly code to check for any unstaged differences of assembly files:
```
python3 (path/to/codeConverter9000/)converter9000.py hephaestus (--withCMake | --withMake)
```

To replace `IMPLICIT DOUBLE(A-H,O-Z)` with `IMPLICIT DOUBLE` in all your `.F90` files run:
```
python3 (path/to/codeConverter9000/)typeParser.py declare .F90 (--withCMake | --withMake) --recursive
```
You can also declare files in a specific folder by replacing `--recursive` with
```
--path=./desired/folder/
```
Or further specify to declare only some files by adding:
```
--only=file1.f,file2.f
```

After the script has type declared a file, check if there are any unstaged assembly differences.

If there aren't any, you can either commit the changes or continue.

If there are unstaged assembly changes, they were introduced by the type declaration. Discard the changes to the file and press any key for the script to continue to the next file.
If you had previously changed files with no assembly difference, commit those before discarding all changes.


## Changing syntax of unsupported DO loops
* **IMPORTANT:** The script will automatically check for assembly differences and if there are none it will make a commit with the title 'Change DO_LOOP in (filename)' where (filename) will be replaced by the name of the fortran file. It would be recommended to not run it on the mater branch but on a seperate one and squish all the DO loop changes into 1 commit afterwards.

To start the script for updating the syntax of DO loops in all .`F90` files run:
```
python3 (path/to/codeConverter9000/)doParser.py declare .F90 (--withCMake | --withMake) --recursive
```
## Changing syntax of arithmetic IF statements
For updating arithmetic IF statements, first make sure you save the inital assembly code by running
```
python3 (path/to/codeConverter9000/)converter9000.py hephaestus .F90 --withCMake
```
Then change the IF statements in the desired folders or files by running:
```
python3 (path/to/codeConverter9000/)ifParser.py parse .F90 --recursive
```
Here you can again add `--path=./somefolder/` to only change files within that folder or replace '--recursive' with `--only=filename1.F90,filename2.F90` for specific files within that folder.

After the IF statements have been updated, you can stage all changes in git, and run the hephaestus command to gather the new assembly code. However, assembly changes might occur simply changing the amount of lines of the code.

[1]:https://www.microsoft.com/en-us/p/ubuntu-2004-lts/9n6svws3rx71?activetab=pivot:overviewtab "Microsoft store page for Ubuntu 20.04 LTS"
[2]:https://github.com/docopt/docopt#help-message-format "docopt github documentation page"
[3]:https://github.com/wvermin/findent "findent github page"
[4]:https://git-scm.com/ "Git home page"
