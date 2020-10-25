import os
import zipfile
from . generic import *
from . addon_files import iterRelativeAddonFiles, iterRelativeExportCFiles, iterRelativeHeaderFiles

currentDirectory = os.path.dirname(os.path.abspath(__file__))

def execute_Export(addonDirectory, exportPath, addonName):
    removeFile(exportPath)

    with zipfile.ZipFile(exportPath, "w", zipfile.ZIP_DEFLATED) as zipFile:
        for relativePath in iterRelativeAddonFiles(addonDirectory):
            absolutePath = os.path.join(addonDirectory, relativePath)
            zipFile.write(absolutePath, os.path.join(addonName, relativePath))

    print("Exported Addon:")
    print("    " + exportPath)

def execute_ExportC(addonDirectory, exportCPath, exportCSetupPath, addonName):
    removeFile(exportCPath)
    topdir = f"{addonName}_c"

    with zipfile.ZipFile(exportCPath, "w", zipfile.ZIP_DEFLATED) as zipFile:
        for relativePath in iterRelativeExportCFiles(addonDirectory):
            absolutePath = os.path.join(addonDirectory, relativePath)
            zipFile.write(absolutePath, os.path.join(topdir, addonName, relativePath))

        for path in iterPathsWithExtension(currentDirectory, ".py"):
            relativePath = os.path.relpath(path, currentDirectory)
            zipFile.write(path, os.path.join(topdir, "_setuputils", relativePath))

        setupInfo = getPlatformSummary()
        tmpFileName = "tmp.json"
        writeJsonFile(tmpFileName, setupInfo)
        zipFile.write(tmpFileName, os.path.join(topdir, "setup_info.json"))
        removeFile(tmpFileName)

        zipFile.write(exportCSetupPath, os.path.join(topdir, "setup.py"))

    print("Exported C Build:")
    print("    " + exportCPath)

def execute_ExportHeaders(addonDirectory, exportHeadersPath, addonName):
    removeFile(exportHeadersPath)
    topdir = f"{addonName}_headers"

    with zipfile.ZipFile(exportHeadersPath, "w", zipfile.ZIP_DEFLATED) as zipFile:
        modulePaths = set()
        for relativePath in iterRelativeHeaderFiles(addonDirectory):
            absolutePath = os.path.join(addonDirectory, relativePath)
            zipFile.write(absolutePath, os.path.join(topdir, addonName, relativePath))

            directory = os.path.dirname(relativePath)
            while directory:
                modulePaths.add(directory)
                directory = os.path.dirname(directory)

        modulePaths.add("")
        for relativePath in modulePaths:
            arcpath = os.path.join(topdir, addonName, relativePath, "__init__.py")
            zipFile.writestr(arcpath, bytes())

    print("Exported Headers:")
    print("    " + exportHeadersPath)
