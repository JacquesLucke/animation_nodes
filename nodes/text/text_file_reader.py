import os
import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

# path : last modification, content
cache = {}

class TextFileReaderNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextFileReaderNode"
    bl_label = "Text File Reader"
    bl_width_default = 170

    errorMessage = StringProperty()

    def create(self):
        self.newInput("String", "Path", "path", showFileChooser = True)
        self.newOutput("String", "Text", "text")

    def draw(self, layout):
        if self.inputs[0].isUnlinked:
            name = os.path.basename(self.inputs[0].value)
            if name != "":
                layout.label(name, icon = "FILE_TEXT")

        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, path):
        self.errorMessage = ""

        if not os.path.exists(path):
            self.errorMessage = "Path does not exist"
            return ""

        lastModification = os.stat(path).st_mtime

        loadFile = False
        if path not in cache:
            loadFile = True
        else:
            oldLastModification = cache[path][0]
            if lastModification > oldLastModification:
                loadFile = True

        if loadFile:
            try:
                with open(path, "rt") as f:
                    data = f.read()
                cache[path] = (lastModification, data)
            except:
                self.errorMessage = "Couldn't read file"

        return cache.get(path, (0, ""))[1]
