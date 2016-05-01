import os
import bpy
import collections
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

# path : last modification, content
cache = {}
pathsByIdentifier = collections.defaultdict(set)

class TextFileReaderNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextFileReaderNode"
    bl_label = "Text File Reader"
    bl_width_default = 170

    def encodingChanged(self, context):
        for path in pathsByIdentifier[self.identifier]:
            del cache[path]
        propertyChanged()

    encoding = StringProperty(name = "Encoding", default = "ascii",
        description = "Encoding used when reading the file (ascii, utf8, ...)",
        update = encodingChanged)

    errorMessage = StringProperty()

    def create(self):
        self.newInput("String", "Path", "path", showFileChooser = True)
        self.newOutput("String", "Text", "text")

    def draw(self, layout):
        if self.inputs[0].isUnlinked:
            name = os.path.basename(self.inputs[0].value)
            if name != "":
                layout.label(name, icon = "FILE_TEXT")

        layout.prop(self, "encoding")

        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, path):
        self.errorMessage = ""

        if not os.path.exists(path):
            self.errorMessage = "Path does not exist"
            return ""

        pathsByIdentifier[self.identifier].add(path)

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
                with open(path, "r", encoding = self.encoding) as f:
                    data = f.read()
                cache[path] = (lastModification, data)
            except LookupError:
                self.errorMessage = "Invalid Encoding"
            except:
                self.errorMessage = "Encoding Error"

        return cache.get(path, (0, ""))[1]
