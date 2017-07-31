import os
import zipfile
from . generic import *
from . addon_files import iterRelativeAddonFiles, iterRelativeExportCFiles

currentDirectory = os.path.dirname(os.path.abspath(__file__))

def execute_Export(addonDirectory, exportPath):
    removeFile(exportPath)

    with zipfile.ZipFile(exportPath, "w", zipfile.ZIP_DEFLATED) as zipFile:
        for relativePath in iterRelativeAddonFiles(addonDirectory):
            absolutePath = os.path.join(addonDirectory, relativePath)
            zipFile.write(absolutePath, os.path.join("animation_nodes", relativePath))

    print("Exported Addon:")
    print("    " + exportPath)

def execute_ExportC(addonDirectory, exportCPath, exportCSetupPath):
    removeFile(exportCPath)
    topdir = "animation_nodes_c"

    with zipfile.ZipFile(exportCPath, "w", zipfile.ZIP_DEFLATED) as zipFile:
        for relativePath in iterRelativeExportCFiles(addonDirectory):
            absolutePath = os.path.join(addonDirectory, relativePath)
            zipFile.write(absolutePath, os.path.join(topdir, "animation_nodes", relativePath))

        for path in iterPathsWithExtension(currentDirectory, ".py"):
            relativePath = os.path.relpath(path, currentDirectory)
            zipFile.write(path, os.path.join(topdir, "setuputils", relativePath))

        setupInfo = getPlatformSummary()
        tmpFileName = "tmp.json"
        writeJsonFile(tmpFileName, setupInfo)
        zipFile.write(tmpFileName, os.path.join(topdir, "setup_info.json"))
        removeFile(tmpFileName)

        zipFile.write(exportCSetupPath, os.path.join(topdir, "setup.py"))

    print("Exported C Build:")
    print("    " + exportCPath)
