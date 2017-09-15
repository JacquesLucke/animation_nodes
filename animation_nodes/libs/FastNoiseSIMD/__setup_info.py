import os
import sys
import subprocess

def getCompileLibraryTasks(utils):
    return [compile_FastNoiseSIMD]

def compile_FastNoiseSIMD(utils):
    print("Compile FastNoiseSIMD\n\n")
    sourceDir = os.path.join(os.path.dirname(__file__), "source")

    _platform = sys.platform
    if _platform.startswith("win"):
        subprocess.run(os.path.join(sourceDir, "compile_windows.bat"))
    elif _platform.startswith("linux"):
        subprocess.run(os.path.join(sourceDir, "compile_linux.sh"))
    elif _platform == "darwin":
        subprocess.run(os.path.join(sourceDir, "compile_macos.sh"))
    else:
        raise Exception("unknown platform, cannot compile")
