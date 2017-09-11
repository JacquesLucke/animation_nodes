import os

__all__ = ["iterRelativeAddonFiles", "iterRelativeExportCFiles"]

def iterRelativeAddonFiles(basepath):
    for root, dirs, files in os.walk(basepath, topdown = True):
        for directory in dirs:
            if isAddonDirectoryIgnored(directory):
                dirs.remove(directory)
        for filename in files:
            if not isAddonFileIgnored(filename):
                fullpath = os.path.join(root, filename)
                yield os.path.relpath(fullpath, basepath)

def iterRelativeExportCFiles(basepath):
    for root, dirs, files in os.walk(basepath, topdown = True):
        for directory in dirs:
            if isAddonDirectoryIgnored(directory):
                dirs.remove(directory)
        for filename in files:
            if not isExportCFileIgnored(filename):
                fullpath = os.path.join(root, filename)
                yield os.path.relpath(fullpath, basepath)

def isAddonDirectoryIgnored(name):
    return name in {".git", "__pycache__"}

def isAddonFileIgnored(name):
    extensions = [".src", ".pxd", ".pyx", ".html", ".c", ".cpp", ".h", ".lib", ".a", ".o", ".obj", ".sh", ".bat"]
    names = {".gitignore", "__setup_info.py"}
    return any(name.endswith(ext) for ext in extensions) or name in names

def isExportCFileIgnored(name):
    extensions = [".src", ".html", ".so", ".pyd"]
    names = {".gitignore", "__setup_info.py", "compilation_info.json"}
    return any(name.endswith(ext) for ext in extensions) or name in names
