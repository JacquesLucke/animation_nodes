import os
from . generic import *
from . addon_files import iterRelativeAddonFiles

def execute_CopyAddon(addonDirectory, targetPath):
    targetPath = os.path.join(targetPath, "animation_nodes")
    printHeader("Copy Addon")
    try:
        changes = syncDirectories(addonDirectory, targetPath, iterRelativeAddonFiles)
    except PermissionError:
        raise Exception("\n\nGot a permission error.\nThis might happen when Blender is open while copying.")

    for path in changes["removed"]:
        print("Removed:", os.path.relpath(path, targetPath))
    for path in changes["updated"]:
        print("Updated:", os.path.relpath(path, targetPath))
    for path in changes["created"]:
        print("Created:", os.path.relpath(path, targetPath))

    totalChanged = sum(len(l) for l in changes.values())
    print("\nModified {} files.".format(totalChanged))
