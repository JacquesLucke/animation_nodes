'''
Command Line Arguments:
    python setup.py
     -all            # recompile all
     -export         # make redistributable version

Generate .html files to debug cython code:
    cython -a filename.pyx

Cleanup Repository:
    git clean -fdx       # make sure you don't have uncommited files!
'''

# The compiled build will be copied to this addon folder.
# Please change it to use this feature.
addonsDirectory = "C:\\Users\\Jacques Lucke\\AppData\\Roaming\\Blender Foundation\\Blender\\2.78\\scripts\\addons"

import sys

v = sys.version_info
if v.major < 3 or v.minor < 5:
    print("Only works with Python 3.5.x")
    print("You are using: {}".format(sys.version))
    sys.exit()

import os
import shutil
from os.path import abspath, dirname, join, relpath

currentDirectory = dirname(abspath(__file__))
sourceDirectory = join(currentDirectory, "animation_nodes")

initialArgs = sys.argv[:]


def main():
    if canCompileCython():
        preprocessor()
        if "-all" in initialArgs:
            removeCFiles()
        compileCythonFiles()
        if "-export" in initialArgs:
            export()
        if os.path.isdir(addonsDirectory):
            copyToBlender()
        else:
            print("The path to Blenders addon directory does not exist")

def canCompileCython():
    if "bpy" in sys.modules:
        return False
    if not os.path.isdir(sourceDirectory):
        return False
    correctSysPath()
    try:
        import Cython
        return True
    except:
        print("Cython is not installed for this Python version.")
        print(sys.version)
        return False

def correctSysPath():
    pathsToRemove = [path for path in sys.path if currentDirectory in path]
    for path in pathsToRemove:
        sys.path.remove(path)
        print("Removed from sys.path:", path)



# Preprocess - execute .pre files
###################################################################

def preprocessor():
    for path in iterPathsWithSuffix(".pre"):
        code = readFile(path)
        codeBlock = compile(code, path, "exec")
        context = {
            "__file__" : abspath(path),
            "readFile" : readFile,
            "writeFile" : writeFile,
            "multiReplace" : multiReplace,
            "dependenciesChanged" : dependenciesChanged,
            "changeFileName" : changeFileName}
        exec(codeBlock, context, context)



# Translate .pyx to .c files and compile extension modules
###################################################################

def compileCythonFiles():
    from distutils.core import setup
    from Cython.Build import cythonize

    sys.argv = [sys.argv[0], "build_ext", "--inplace"]

    extensions = cythonize(getPathsToCythonFiles())
    setup(name = 'Animation Nodes', ext_modules = extensions)
    print("Compilation Successful.")

def getPathsToCythonFiles():
    return list(iterPathsWithSuffix(".pyx"))

def removeCFiles():
    for path in iterPathsWithSuffix(".c"):
        os.remove(path)
    print("Remove generated .c files.")



# Copy to Blenders addons directory
###################################################################

def copyToBlender():
    print("\n\nCopy changes to addon folder")
    targetPath = join(addonsDirectory, "animation_nodes")
    copyAddonFiles(sourceDirectory, targetPath, verbose = True)
    print("\nCopied all changes")



# Export Build
###################################################################

def export():
    print("\nStart Export")

    targetPath = join(currentDirectory, "animation_nodes.zip")
    zipAddonDirectory(sourceDirectory, targetPath)

    print("Finished Export")
    print("Zipped file can be found here:")
    print("  " + targetPath)



# Copy Addon Utilities
###################################################################

def copyAddonFiles(source, target, verbose = False):
    if not os.path.isdir(target):
        os.mkdir(target)

    existingFilesInSource = set(iterRelativeAddonFiles(source))
    existingFilesInTarget = set(iterRelativeAddonFiles(target))

    counter = 0

    filesToRemove = existingFilesInTarget - existingFilesInSource
    for relativePath in filesToRemove:
        path = join(target, relativePath)
        removeFile(path)
        if verbose: print("Removed File: ", path)
        counter += 1

    filesToCreate = existingFilesInSource - existingFilesInTarget
    for relativePath in filesToCreate:
        sourcePath = join(source, relativePath)
        targetPath = join(target, relativePath)
        copyFile(sourcePath, targetPath)
        if verbose: print("Created File: ", targetPath)
        counter += 1

    filesToUpdate = existingFilesInSource.intersection(existingFilesInTarget)
    for relativePath in filesToUpdate:
        sourcePath = join(source, relativePath)
        targetPath = join(target, relativePath)
        sourceModificationTime = os.stat(sourcePath).st_mtime
        targetModificationTime = os.stat(targetPath).st_mtime
        if sourceModificationTime > targetModificationTime:
            overwriteFile(sourcePath, targetPath)
            if verbose: print("Updated File: ", targetPath)
            counter += 1

    print("Changed {} files.".format(counter))

def removeFile(path):
    try:
        os.remove(path)
    except:
        if tryGetFileAccessPermission(path):
            os.remove(path)

def copyFile(source, target):
    directory = dirname(target)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    shutil.copyfile(source, target)

def overwriteFile(source, target):
    removeFile(target)
    copyFile(source, target)


def iterRelativeAddonFiles(directory):
    if not os.path.isdir(directory):
        return

    for root, folders, files in os.walk(directory, topdown = True):
        for folder in folders:
            if ignoreAddonDirectory(folder):
                folders.remove(folder)

        for fileName in files:
            if not ignoreAddonFile(fileName):
                yield relpath(join(root, fileName), directory)


def ignoreAddonFile(name):
    return name.endswith(".c")

def ignoreAddonDirectory(name):
    return name in {".git", "__pycache__"}

def tryRemoveDirectory(path):
    try: shutil.rmtree(path, onerror = handlePermissionError)
    except FileNotFoundError: pass

def handlePermissionError(function, path, excinfo):
    if tryGetFileAccessPermission(path):
        function(path)
    else:
        raise

def tryGetFileAccessPermission(path):
    import stat
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        return True
    return False

def zipAddonDirectory(sourcePath, targetPath):
    try: os.remove(targetPath)
    except FileNotFoundError: pass

    import zipfile
    with zipfile.ZipFile(targetPath, "w", zipfile.ZIP_DEFLATED) as zipFile:
        for relativePath in iterRelativeAddonFiles(sourcePath):
            absolutePath = join(sourcePath, relativePath)
            zipFile.write(absolutePath, relativePath)



# Utils
###################################################################

def iterPathsWithSuffix(suffix):
    for root, dirs, files in os.walk(sourceDirectory):
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

main()
