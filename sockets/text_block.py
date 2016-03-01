import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket

class TextBlockSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_TextBlockSocket"
    bl_label = "Text Block Socket"
    dataType = "Text Block"
    allowedInputTypes = ["Text Block"]
    drawColor = (0.5, 0.5, 0.5, 1)
    storable = False
    hashable = True

    textBlockName = StringProperty(update = propertyChanged)

    def drawProperty(self, layout, text):
        layout.prop_search(self, "textBlockName",  bpy.data, "texts", text = text)

    def getValue(self):
        return bpy.data.texts.get(self.textBlockName)

    def setProperty(self, data):
        self.textBlockName = data

    def getProperty(self):
        return self.textBlockName
