import os
import sys
import json
from distutils.core import Extension, setup

currentDirectory = os.path.dirname(os.path.abspath(__file__))
setupInfoPath = os.path.join(currentDirectory, "setup_info.json")
compilationInfoPath = os.path.join(currentDirectory, "animation_nodes", "compilation_info.json")

with open(setupInfoPath, "rt") as f:
    setupInfo = json.loads(f.read())

extensions = []
for info in setupInfo["Extensions"]:
    sources = []
    for sourceParts in info["Sources"]:
        relativeSource = os.path.join(*sourceParts)
        sources.append(os.path.join(currentDirectory, relativeSource))
    extensions.append(Extension(info["Module Name"], sources))

sys.argv = [sys.argv[0], "build_ext", "--inplace"]
setup(
    ext_modules = extensions
)

compilationInfo = {
    "sys.version" : sys.version,
    "sys.platform" : sys.platform,
    "sys.api_version" : sys.api_version,
    "sys.version_info" : sys.version_info,
    "os.name" : os.name,
    "Cython.__version__" : setupInfo["Cython.__version__"]
}

with open(compilationInfoPath, "wt") as f:
    f.write(json.dumps(compilationInfo, indent = 4, sort_keys = True))
