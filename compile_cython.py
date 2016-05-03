# Install VS 2015 first with the c++ common tools
# Some commands for easy reference:
#   cython -a yourmod.pyx
#   python setup.py build_ext --inplace

import os
import sys
import shutil
from io import StringIO
from contextlib import redirect_stdout
from os.path import abspath, dirname, basename, join

currentDirectory = dirname(abspath(__file__))

# should be 'animation_nodes' or 'animation_nodes-master' most of the time
currentDirectoryName = basename(currentDirectory)


def main():
    if canCompileCython():
        compileCythonFiles()

def canCompileCython():
    try:
        import Cython
        return True
    except:
        return False

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
        print("Compilation Successful")
        print("More information is in the '.compilation_log' file")
    except:
        print(resultBuffer.getvalue())

    with open(".compilation_log", "wt") as logFile:
        logFile.write(resultBuffer.getvalue())

    cleanupRepository()

def getPathsToCythonFiles():
    return list(iterPathsWithSuffix(".pyx"))

def iterPathsWithSuffix(suffix):
    for root, dirs, files in os.walk("."):
        for fileName in files:
            if fileName.endswith(suffix):
                yield join(root, fileName)

def cleanupRepository():
    buildDirectory = join(currentDirectory, "build")
    if os.path.exists(buildDirectory):
        shutil.rmtree(buildDirectory)

main()
