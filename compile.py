'''
Compiling the cython code needs some setup (only tested on windows yet):

    1. Install Anaconda: https://www.continuum.io/downloads (Python 3.5)
       If you have another python version already installed make sure that
       the command line uses the right version. You can check this by executing
       this command: 'python -V'
       The result should be something like: 'Python 3.5.1 :: Anaconda 2.5.0 (64-bit)'

    2. Install cython with this command: 'conda install cython'

    3. Navigate to the 'animation_nodes' folder in the command line and
       execute 'python compile.py'. If you are lucky this works immediatly..
       It didn't work for me directly. Oftentimes there is an error message like this:
       'unable to find vcvarsall.bat'.
       To fix this you need install Visual Studio 2015 Community, especially
       the 'Common Tools for Visual C++ 2015' as you can see here:
       http://stackoverflow.com/a/35243904/4755171
       This can take a while, but in the end you should be able to run this file..
       Please report any issue you have.

Command Line Arguments:
    python compile.py            # full cleanup afterwards
    python compile.py -c         # don't remove generated .c file

Generate .html files to debug cython code:
    cython -a filename.pyx

Cleanup Repository:
    git clean -fdx
'''

import sys

v = sys.version_info
if v.major < 3 or v.minor < 5:
    print("Only works with Python 3.5.x")
    print("You are using: {}".format(sys.version))
    sys.exit()

import os
import re
import shutil
from io import StringIO
from itertools import chain
from contextlib import redirect_stdout
from os.path import abspath, dirname, basename, join

currentDirectory = dirname(abspath(__file__))

# should be 'animation_nodes' or 'animation_nodes-master' most of the time
currentDirectoryName = basename(currentDirectory)

initialArgs = sys.argv[:]


def main():
    if canCompileCython():
        preprocessor()
        compileCythonFiles()

def canCompileCython():
    if "bpy" in sys.modules:
        return False
    try:
        import Cython
        return True
    except:
        print("Cython is not installed for this Python version.")
        print(sys.version)
        return False



# Preprocess and convert .pyxt to .pyx files
###################################################################

def preprocessor():
    for path in iterPathsWithSuffix(".pre"):
        code = readFile(path)
        codeBlock = compile(code, path, "exec")
        context = {
            "__file__" : abspath(path),
            "baseListsParameters" : baseListsParameters,
            "complexListsParameters" : complexListsParameters,
            "readFile" : readFile,
            "writeFile" : writeFile,
            "multiReplace" : multiReplace,
            "dependenciesChanged" : dependenciesChanged,
            "changeFileName" : changeFileName}
        exec(codeBlock, context, context)



# Translate .pyx to .c files and compile extension modules
###################################################################

def compileCythonFiles():
    import Cython
    from distutils.core import setup
    from Cython.Build import cythonize

    sys.argv = [sys.argv[0], "build_ext", "--inplace"]

    extensions = cythonize(getPathsToCythonFiles())
    for extension in extensions:
        # cut off 'animation_nodes.' from name
        extension.name = extension.name[len(currentDirectoryName)+1:]


    resultBuffer = StringIO()
    try:
        with redirect_stdout(resultBuffer):
            setup(name = 'AN Cython', ext_modules = extensions)
        print("Compilation Successful.")
        print("More information is in the '.log' file.")
    except:
        print(resultBuffer.getvalue())

    writeFile(".log", resultBuffer.getvalue())

    cleanupRepository(
        removeBuildDirectory = True,
        removeCFiles = "-c" in initialArgs)

def getPathsToCythonFiles():
    return list(iterPathsWithSuffix(".pyx"))

def cleanupRepository(removeBuildDirectory, removeCFiles):
    if removeBuildDirectory:
        buildDirectory = join(currentDirectory, "build")
        if os.path.exists(buildDirectory):
            shutil.rmtree(buildDirectory)
        print("Removed not needed build directory.")
    if removeCFiles:
        for path in iterPathsWithSuffix(".c"):
            os.remove(path)
        print("Remove generated .c files.")



# Utils
###################################################################

def iterPathsWithSuffix(suffix):
    for root, dirs, files in os.walk("."):
        for fileName in files:
            if fileName.endswith(suffix):
                yield join(root, fileName)

def writeFile(path, content):
    with open(path, "wt") as f:
        f.write(content)
    print("Changed File:", path)

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def changeFileName(path, newName):
    return join(dirname(path), newName)

def multiReplace(text, **replacements):
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text

def dependenciesChanged(target, dependencies):
    try: targetTime = os.stat(target).st_mtime
    except FileNotFoundError: targetTime = 0
    latestDependencyModification = max(os.stat(path).st_mtime for path in dependencies)
    return targetTime < latestDependencyModification

baseListsParameters = [
    ("FloatList", "float"),
    ("DoubleList", "double"),
    ("CharList", "char"),          ("UCharList", "unsigned char"),
    ("LongList", "long"),          ("ULongList", "unsigned long"),
    ("IntegerList", "int"),        ("UIntegerList", "unsigned int"),
    ("ShortList", "short"),        ("UShortList", "unsigned short"),
    ("LongLongList", "long long"), ("ULongLongList", "unsigned long long")
]

complexListsParameters = [
    dict(BASELISTTYPE = "FloatList",
         LISTNAME = "VectorList",
         BASETYPE = "float",
         AMOUNT = "3")
]

main()
