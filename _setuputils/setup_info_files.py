from . generic import *

def getSetupInfoList(addonDirectory):
    setupInfoList = []
    for path in iterSetupInfoPaths(addonDirectory):
        setupInfoList.append(executePythonFile(path))
    return setupInfoList

def iterSetupInfoPaths(addonDirectory):
    return iterPathsWithFileName(addonDirectory, "__setup_info.py")
