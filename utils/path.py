import bpy
import os

def toAbsolutePath(path, start = None, library = None):
    absPath = bpy.path.abspath(path, start, library)
    return os.path.normpath(absPath)