import os
import sys

currentDirectory = os.path.dirname(os.path.abspath(__file__))

if not os.path.samefile(currentDirectory, os.getcwd()):
    print("You are not in the correct directory.")
    print("Expected:", currentDirectory)
    print("Got:     ", os.getcwd())
    sys.exit()

if currentDirectory not in sys.path:
    sys.path.append(currentDirectory)

addonName = "animation_nodes"
addonDirectory = os.path.join(currentDirectory, addonName)
exportPath = os.path.join(currentDirectory, "{}.zip".format(addonName))

from _setuputils.export import execute_Export
from _setuputils.compilation import execute_Compile
from _setuputils.compile_libraries import execute_CompileLibraries
from _setuputils.setup_info_files import getSetupInfoList

setupInfoList = getSetupInfoList(addonDirectory)

execute_CompileLibraries(setupInfoList, addonDirectory)
execute_Compile(setupInfoList, addonDirectory)
execute_Export(addonDirectory, exportPath, addonName)

print("\nDone.")
