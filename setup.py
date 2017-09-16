import os
import sys
import json
import textwrap
import subprocess
from pprint import pprint

currentDirectory = os.path.dirname(os.path.abspath(__file__))

if not os.path.samefile(currentDirectory, os.getcwd()):
    print("You are not in the correct directory.")
    print("Expected:", currentDirectory)
    print("Got:     ", os.getcwd())
    sys.exit()

if currentDirectory not in sys.path:
    sys.path.append(currentDirectory)

from _setuputils.generic import *
from _setuputils.addon_files import *
from _setuputils.cythonize import execute_Cythonize
from _setuputils.compilation import execute_Compile
from _setuputils.copy_addon import execute_CopyAddon
from _setuputils.pypreprocess import execute_PyPreprocess
from _setuputils.setup_info_files import getSetupInfoList
from _setuputils.export import execute_Export, execute_ExportC
from _setuputils.compile_libraries import execute_CompileLibraries

addonName = "animation_nodes"
addonDirectory = os.path.join(currentDirectory, addonName)
defaultConfigPath = os.path.join(currentDirectory, "conf.default.json")
configPath = os.path.join(currentDirectory, "conf.json")
exportPath = os.path.join(currentDirectory, "{}.zip".format(addonName))
exportCPath = os.path.join(currentDirectory, "{}_c.zip".format(addonName))
exportCSetupPath = os.path.join(currentDirectory, "_export_c_setup.py")

possibleCommands = ["build", "help", "clean"]

buildOptionDescriptions = [
    ("--copy", "Copy build to location specified in the conf.json file"),
    ("--export", "Create installable .zip file"),
    ("--exportc", "Create build that can be compiled without cython"),
    ("--nocompile", "Don't compile the extension modules"),
    ("--noversioncheck", "Don't check the used Python version")
]
buildOptions = {option for option, _ in buildOptionDescriptions}
helpNote = "Use 'python setup.py help' to see the possible commands."


# Main
####################################################

def main():
    configs = setupConfigFile()
    args = sys.argv[1:]
    if len(args) == 0 or args[0] == "help":
        main_Help()
    elif args[0] == "build":
        main_Build(args[1:], configs)
    elif args[0] == "clean":
        main_Clean()
    else:
        print("Invalid command: '{}'\n".format(args[0]))
        print(helpNote)
        sys.exit()

def setupConfigFile():
    if not fileExists(defaultConfigPath):
        print("Expected conf.default.json file to exist.")
        sys.exit()
    if not fileExists(configPath):
        copyFile(defaultConfigPath, configPath)
        print(textwrap.dedent('''\
        Copied the conf.default.json file to conf.json.
        Please change it manually if needed.
        Note: git ignorers it, so depending on the settings of your editor
              it might not be shows inside it.
        '''))
    return readJsonFile(configPath)


# Help
####################################################

def main_Help():
    print(textwrap.dedent('''\
    usage: python setup.py <command> [options]

    Possible commands:
        help                Show this help
        build               Build the addon from sources
        clean               Remove all untracked files except conf.py

    The 'build' command has multiple options:'''))
    for option, description in buildOptionDescriptions:
        print("    {:20}{}".format(option, description))


# Clean
####################################################

def main_Clean():
    answer = input("Remove all files? [y/n] ").lower()
    print()
    if answer == "y":
        removedFiles = removeUntrackedFiles(filesToKeep = ["conf.json"])["removed"]
        print("Cleanup Finished.")
        print("Removed {} files.".format(len(removedFiles)))
    else:
        print("Operation canceled.")
        sys.exit()

@returnChangedFileStates(currentDirectory)
def removeUntrackedFiles(filesToKeep):
    storedFiles = {}
    for path in filesToKeep:
        if fileExists(path):
            storedFiles[path] = readBinaryFile(path)

    try:
        pipe = subprocess.PIPE
        subprocess.run(["git", "clean", "-fdx"], stdout = pipe, stderr = pipe)
    except FileNotFoundError:
        print("git is required but not installed")
        sys.exit()

    for path, content in storedFiles.items():
        writeBinaryFile(path, content)



# Build
####################################################

def main_Build(options, configs):
    checkBuildEnvironment(
        checkCython = True,
        checkPython = "--noversioncheck" not in options and "--nocompile" not in options
    )
    checkBuildOptions(options)

    changedFileStates = build(skipCompilation = "--nocompile" in options)
    printChangedFileStates(changedFileStates, currentDirectory)

    if "--copy" in options:
        copyTarget = configs["Copy Target"]
        if not directoryExists(copyTarget):
            print("Copy Target not found. Please correct the conf.json file.")
        else:
            execute_CopyAddon(addonDirectory, configs["Copy Target"], addonName)
            print()
    if "--export" in options:
        execute_Export(addonDirectory, exportPath, addonName)
    if "--exportc" in options:
        execute_ExportC(addonDirectory, exportCPath, exportCSetupPath, addonName)

def printChangedFileStates(states, basepath):
    printHeader("File System Changes")

    print("New Files:")
    printIndentedPathList(states["new"], basepath)
    print("\nRemoved Files:")
    printIndentedPathList(states["removed"], basepath)
    print("\nModified Files:")
    printIndentedPathList(states["changed"], basepath)

def printIndentedPathList(paths, basepath):
    if len(paths) == 0:
        print("  <none>")
    else:
        for path in sorted(paths):
            print("  {}".format(os.path.relpath(path, basepath)))

@returnChangedFileStates(currentDirectory)
def build(skipCompilation = False):
    setupInfoList = getSetupInfoList(addonDirectory)

    execute_PyPreprocess(setupInfoList, addonDirectory)
    execute_Cythonize(setupInfoList, addonDirectory)

    if not skipCompilation:
        execute_CompileLibraries(setupInfoList, addonDirectory)
        execute_Compile(setupInfoList, addonDirectory)

def checkBuildEnvironment(checkCython, checkPython):
    if checkCython:
        try: import Cython
        except:
            print("Cython is not installed for this Python version.")
            print(sys.version)
            sys.exit()
    if checkPython:
        v = sys.version_info
        if v.major != 3 or v.minor != 5:
            print(textwrap.dedent('''\
            Blender 2.78/2.79 officially uses Python 3.5.x.
            You are using: {}

            Use the --noversioncheck option to disable this check.\
            '''.format(sys.version)))
            sys.exit()

def checkBuildOptions(options):
    options = set(options)
    invalidOptions = options - buildOptions
    if len(invalidOptions) > 0:
        print("Invalid build options: {}\n".format(invalidOptions))
        print(helpNote)
        sys.exit()

    if "--nocompile" in options:
        if "--copy" in options:
            print("The options --nocompile and --copy don't work together.")
            sys.exit()
        if "--export" in options:
            print("The options --nocompile and --export don't work together.")
            sys.exit()


# Run Main
###############################################

main()
