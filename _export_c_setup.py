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

addonDirectory = os.path.join(currentDirectory, "animation_nodes")
exportPath = os.path.join(currentDirectory, "animation_nodes.zip")

from setuputils.logger import Logger
from setuputils.export import execute_Export
from setuputils.compilation import execute_Compile
from setuputils.setup_info_files import getSetupInfoList

logger = Logger()
setupInfoList = getSetupInfoList(addonDirectory)
execute_Compile(setupInfoList, logger, addonDirectory)
execute_Export(addonDirectory, exportPath)

print("\nDone.")
