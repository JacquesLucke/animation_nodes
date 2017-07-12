'''
Copyright (C) 2016 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

'''
Command Line Arguments:
    python setup.py
     --all            # recompile all
     --export         # make redistributable version
     --nocopy         # don't copy the build into Blenders addon directory

Generate .html files to debug cython code:
    cython -a path/to/file.pyx

Cleanup Repository:
    git clean -fdx       # make sure you don't have uncommited files!
'''

import os
import sys
import shutil
import traceback
from os.path import abspath, dirname, join, relpath

addonName = "animation_nodes"
currentDirectory = dirname(abspath(__file__))
sourceDirectory = join(currentDirectory, addonName)
configPath = join(currentDirectory, "config.py")
defaultConfigPath = join(currentDirectory, "config.default.py")
compilationInfoPath = join(sourceDirectory, "compilation_info.json")

config = {}

initialArgs = sys.argv[:]

expectedArgs = {"--all", "--export", "--nocopy", "--noversioncheck"}
unknownArgs = set(initialArgs[1:]) - expectedArgs
if len(unknownArgs) > 0:
    print("Unknown arguments:", unknownArgs)
    print("Allowed arguments:", expectedArgs)
    sys.exit()


v = sys.version_info
if "--noversioncheck" not in initialArgs and (v.major != 3 or v.minor != 5):
    print("Blender 2.78/2.79 officially uses Python 3.5.x.")
    print("You are using: {}".format(sys.version))
    print()
    print("Use the --noversioncheck argument to disable this check.")
    sys.exit()
else:
    print(sys.version)
    print()

def main():
    setupAndReadConfigFile()
    if canCompile():
        preprocessor()
        if "--all" in initialArgs:
            removeCFiles()
            removeCompiledFiles()
        compileCythonFiles()
        writeCompilationInfoFile()
        if "--export" in initialArgs:
            export()
        if not "--nocopy" in initialArgs:
            if os.path.isdir(config["addonsDirectory"]):
                copyToBlender()
            else:
                print("The path to Blenders addon directory does not exist")
                print("Please correct the config.py file.")

def setupAndReadConfigFile():
    if not os.path.isfile(configPath) and os.path.isfile(defaultConfigPath):
        shutil.copyfile(defaultConfigPath, configPath)
        print("Copied the config.default.py file to config.py")
        print("Please change it manually if needed.")
        print("Note: git ignores it, so depending on the settings of your editor")
        print("      it might not be shown inside it.\n\n")

    if os.path.isfile(configPath):
        configCode = readFile(configPath)
        exec(configCode, config, config)
    else:
        print("Cannot find any of these files: config.py, config.default.py ")
        print("Make sure that at least the config.default.py exists.")
        print("Maybe you have to clone the repository again.")
        sys.exit()

def canCompile():
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

def removeCompiledFiles():
    for path in iterPathsWithSuffix(".so"):
        os.remove(path)
    for path in iterPathsWithSuffix(".pyd"):
        os.remove(path)
    print("Remove compiled files.")



# Compilation Info File
###################################################################

def writeCompilationInfoFile():
    import Cython

    info = {}
    info["sys.version"] = sys.version
    info["sys.platform"] = sys.platform
    info["sys.api_version"] = sys.api_version
    info["sys.version_info"] = sys.version_info
    info["Cython.__version__"] = Cython.__version__
    info["os.name"] = os.name

    import json
    with open(compilationInfoPath, "w") as f:
        f.write(json.dumps(info, indent = 4))
    print("Save compilation info.")


# Copy to Blenders addons directory
###################################################################

def copyToBlender():
    print("\n\nCopy changes to addon folder")
    targetPath = join(config["addonsDirectory"], addonName)
    try:
        copyAddonFiles(sourceDirectory, targetPath, verbose = True)
    except PermissionError:
        traceback.print_exc()
        print("\n\nMaybe this error happens because Blender is running.")
        sys.exit()
    print("\nCopied all changes")



# Export Build
###################################################################

def export():
    print("\nStart Export")

    targetPath = join(currentDirectory, addonName + ".zip")
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
    return name.endswith(".c") or name.endswith(".html")

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
            zipFile.write(absolutePath, join(addonName, relativePath))



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
