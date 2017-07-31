import os
import zipfile
from . generic import *
from . addon_files import iterRelativeAddonFiles, iterRelativeExportCFiles

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

    with zipfile.ZipFile(exportCPath, "w", zipfile.ZIP_DEFLATED) as zipFile:
        for relativePath in iterRelativeExportCFiles(addonDirectory):
            absolutePath = os.path.join(addonDirectory, relativePath)
            zipFile.write(absolutePath, os.path.join("animation_nodes", relativePath))

        setupInfo = getPlatformSummary()
        tmpFileName = "tmp.json"
        writeJsonFile(tmpFileName, setupInfo)
        zipFile.write(tmpFileName, "setup_info.json")
        removeFile(tmpFileName)

        zipFile.write(exportCSetupPath, "setup.py")

    print("Exported C Build:")
    print("    " + exportCPath)
