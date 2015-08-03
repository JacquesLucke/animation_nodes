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

    textBlockName = StringProperty(update = propertyChanged)
    showName = BoolProperty(default = True)

    def drawInput(self, layout, node, text):
        row = layout.row(align = True)
        if not self.showName: text = ""

        row.prop_search(self, "textBlockName",  bpy.data, "texts", icon="NONE", text = text)

    def getValue(self):
        return bpy.data.texts.get(self.textBlockName)

    def setStoreableValue(self, data):
        self.textBlockName = data
        
    def getStoreableValue(self):
        return self.textBlockName
