# Install VS 2015 first with the c++ common tools
# Some commands for easy reference:
#   cython -a yourmod.pyx
#   python setup.py build_ext --inplace

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


def main():
    if canCompileCython():
        preprocessor()
        compileCythonFiles()

def canCompileCython():
    try:
        import Cython
        return True
    except:
        return False



# Preprocess and convert .pyxt to .pyx files
###################################################################

def preprocessor():
    for path in chain(iterPathsWithSuffix(".pyxt"), iterPathsWithSuffix(".pxdt")):
        content = readFile(path)
        lines = content.splitlines()

        output = []
        outputName = None
        for line in lines:
            if line.startswith("##OUTPUT"):
                outputName = preprocess_OUTPUT(line, path)
            elif line.startswith("##INSERT"):
                output.append(preprocess_INSERT(line, path))
            else:
                output.append(line)

        if outputName is None:
            raise Exception("Output name not specified in " + path)
        outputPath = changeFileName(path, outputName)
        writeFile(outputPath, "\n".join(output))
        print("Created " + outputPath)

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
    return insertContent



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

    cleanupRepository(removeBuildDirectory = True, removeCFiles = True)

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
