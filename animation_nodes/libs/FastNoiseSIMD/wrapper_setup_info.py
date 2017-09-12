import os
import sys
from textwrap import dedent

directory = os.path.dirname(__file__)
libraryDir = os.path.join(directory, "source")

def getExtensionArgs(utils):
    _platform = sys.platform
    if _platform.startswith("win"):
        args = getWindowsArgs(utils)
    elif _platform.startswith("linux"):
        args = getLinuxArgs(utils)
    elif _platform == "darwin":
        args = getMacosArgs(utils)

    args["library_dirs"] = [libraryDir]
    return args

def getWindowsArgs(utils):
    if not utils.fileExists(os.path.join(libraryDir, "FastNoiseSIMD_windows.lib")):
        raise Exception(errorMessage)

    return {
        "libraries" : ["FastNoiseSIMD_windows"],
        "extra_link_args" : ["/NODEFAULTLIB:LIBCMT"]
    }

def getLinuxArgs(utils):
    if not utils.fileExists(os.path.join(libraryDir, "libFastNoiseSIMD_linux.a")):
        raise Exception(errorMessage)

    return {
        "libraries" : ["FastNoiseSIMD_linux"],
        "extra_compile_args" : ["-std=c++11"]
    }

def getMacosArgs(utils):
    raise Exception("MacOS is not yet supported")

    return {
        "libraries" : ["FastNoiseSIMD_macos"]
    }

errorMessage = dedent("""

    A precompiled static library of the FastNoiseSIMD library has not been found.
    Please compile it by running the correct compilation script in this folder:
        {}
    """.format(libraryDir))
