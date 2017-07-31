import os
import re
import io
import sys
import stat
import json
import glob
import shutil
import zipfile
import pathlib
import textwrap
import contextlib

currentDirectory = os.path.dirname(os.path.abspath(__file__))

if not os.path.samefile(currentDirectory, os.getcwd()):
    print("You are not in the correct directory.")
    print("Expected:", currentDirectory)
    print("Got:     ", os.getcwd())
    sys.exit()

if currentDirectory not in sys.path:
    sys.path.append(currentDirectory)

from setuputils.generic import *
from setuputils.addon_files import *
from setuputils.logger import Logger
from setuputils.task import GenerateFileTask
from setuputils.cythonize import execute_Cythonize
from setuputils.compilation import execute_Compile
from setuputils.copy_addon import execute_CopyAddon
from setuputils.pypreprocess import execute_PyPreprocess
from setuputils.setup_info_files import getSetupInfoList
from setuputils.export import execute_Export, execute_ExportC

addonDirectory = os.path.join(currentDirectory, "animation_nodes")
summaryPath = os.path.join(currentDirectory, "setup_summary.json")
defaultConfigPath = os.path.join(currentDirectory, "conf.default.json")
configPath = os.path.join(currentDirectory, "conf.json")
exportPath = os.path.join(currentDirectory, "animation_nodes.zip")
exportCPath = os.path.join(currentDirectory, "animation_nodes_c.zip")
exportCSetupPath = os.path.join(currentDirectory, "_export_c_setup.py")

possibleCommands = ["build", "clean", "help"]

buildOptionDescriptions = [
    ("--copy", "Copy build to location specified in the conf.json file"),
    ("--force", "Rebuild everything"),
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
        clean               Remove generated files

    The 'build' command has multiple options:'''))
    for option, description in buildOptionDescriptions:
        print("    {:20}{}".format(option, description))


# Build
####################################################

def main_Build(options, configs):
    checkBuildEnvironment(
        checkCython = True,
        checkPython = "--noversioncheck" not in options and "--nocompile" not in options
    )
    checkBuildOptions(options)

    if "--force" in options and fileExists(summaryPath):
        main_Clean()

    logger = Logger()
    setupInfoList = getSetupInfoList(addonDirectory)

    execute_PyPreprocess(setupInfoList, logger, addonDirectory)
    execute_Cythonize(setupInfoList, logger, addonDirectory)

    if "--nocompile" not in options:
        execute_Compile(setupInfoList, logger, addonDirectory)

    execute_PrintSummary(logger)
    execute_SaveSummary(logger)

    if "--copy" in options:
        copyTarget = configs["Copy Target"]
        if not directoryExists(copyTarget):
            print("\nCopy Target not found. Please correct the conf.json file.")
        else:
            execute_CopyAddon(addonDirectory, configs["Copy Target"])
    if "--export" in options:
        execute_Export(addonDirectory, exportPath)
    if "--exportc" in options:
        execute_ExportC(addonDirectory, exportCPath, exportCSetupPath)

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


# Clean
####################################################

def main_Clean():
    if not fileExists(summaryPath):
        print("No summary of previous compilation found.")
        sys.exit()

    summary = readJsonFile(summaryPath)
    for path in summary["Generated Files"]:
        if fileExists(path):
            removeFile(path)
            print("Removed:", path)

    buildDirectory = os.path.join(currentDirectory, "build")
    if directoryExists(buildDirectory):
        removeDirectory(buildDirectory)
        print("Removed build directory")


# Summary
###########################################

def execute_PrintSummary(logger):
    printHeader("Summary")

    changedPaths = logger.getChangedFiles()
    for path in changedPaths:
        print("Changed: " + os.path.relpath(path, currentDirectory))

    print("\n{} files changed".format(len(changedPaths)))


# Save Summary
###########################################

def execute_SaveSummary(logger):
    summary = getSummary(logger)
    writeJsonFile(summaryPath, summary)
    print("\nSave Summary: " + os.path.basename(summaryPath))

def getSummary(logger):
    return {
        "PyPreprocess" : getPyPreprocessSummary(logger),
        "Cythonize" : getCythonizeSummary(logger),
        "Compilation" : getCompilationSummary(logger),
        "Platform" : getPlatformSummary(),
        "Generated Files" : logger.getGeneratedFiles()
    }

def getPyPreprocessSummary(logger):
    return [task.getSummary() for task in logger.pyPreprocessTasks]

def getCythonizeSummary(logger):
    return [task.getSummary() for task in logger.cythonizeTasks]

def getCompilationSummary(logger):
    return [task.getSummary() for task in logger.compilationTasks]


# Run Main
###############################################

main()
