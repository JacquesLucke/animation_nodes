'''
Compiling the cython code needs some setup (only tested on windows yet):

    1. Install Anaconda: https://www.continuum.io/downloads (Python 3.5)
       If you have another python version already installed make sure that
       the command line uses the right version. You can check this by executing
       this command: 'python -V'
       The result should be something like: 'Python 3.5.1 :: Anaconda 2.5.0 (64-bit)'

    2. Install cython with this command: 'conda install cython'

    3. Navigate to the 'animation_nodes' folder in the command line and
       execute 'python compile_cython.py'. If you are lucky this works immediatly..
       It didn't work for me directly. Oftentimes there is an error message like this:
       'unable to find vcvarsall.bat'.
       To fix this you need install Visual Studio 2015 Community, especially
       the 'Common Tools for Visual C++ 2015' as you can see here:
       http://stackoverflow.com/a/35243904/4755171
       This can take a while, but in the end you should be able to run this file..
       Please report any issue you have.

Command Line Arguments:
    python compile_cython.py            # full cleanup afterwards
    python compile_cython.py -c         # don't remove generated .c file

Generate .html files to debug cython code:
    cython -a filename.pyx

Cleanup Repository:
    git clean -fdx
'''

import os
import re
import sys
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
    # Will be false when cython is not installed
    # -> won't try to compile when executed from within Blender
    try:
        import Cython
        return True
    except:
        return False



# Preprocess and convert .pyxt to .pyx files
###################################################################

def preprocessor():
    for path in chain(iterPathsWithSuffix(".pyxt"), iterPathsWithSuffix(".pxdt")):
        lastModificationTime = os.stat(path).st_mtime

        content = readFile(path)
        lines = content.splitlines()

        output = []
        output.append("'''")
        output.append("Don't modify this file! It is auto-generated.")
        output.append("All changes will gone after compilation.")
        output.append("The source is here:")
        output.append("  " + path)
        output.append("'''")
        outputName = None
        for line in lines:
            if line.startswith("##OUTPUT"):
                outputName = preprocess_OUTPUT(line, path)
            elif line.startswith("##INSERT"):
                lastSourceModification, insertedCode = preprocess_INSERT(line, path)
                lastModificationTime = max(lastModificationTime, lastSourceModification)
                output.append(insertedCode)
            else:
                output.append(line)

        if outputName is None:
            raise Exception("Output name not specified in " + path)

        outputPath = changeFileName(path, outputName)

        try: lastCreationTime = os.stat(outputPath).st_mtime
        except: lastCreationTime = 0

        if lastModificationTime > lastCreationTime:
            writeFile(outputPath, "\n".join(output))
            print("Created " + outputPath)
        else:
            print("File is up to date: " + outputPath)

def preprocess_OUTPUT(line, path):
    match = re.fullmatch(r"##OUTPUT\s*(.*)\s*", line)
    if match is None:
        raise Exception("Wrong ##OUTPUT in " + path)
    return match.group(1)

def preprocess_INSERT(line, path):
    match = re.fullmatch(r"##INSERT\s*(\w*\.\w*)\s*(\{.*\})", line)
    if match is None:
        raise Exception("Wrong ##INSERT in " + path)
    insertPath = changeFileName(path, match.group(1))
    insertContent = readFile(insertPath)
    replaceDict = eval(match.group(2))
    for key, value in replaceDict.items():
        insertContent = insertContent.replace(key, value)
    return os.stat(insertPath).st_mtime, insertContent



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
        removeCFiles = "-c" not in initialArgs)

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

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def changeFileName(path, newName):
    return join(dirname(path), newName)

main()
