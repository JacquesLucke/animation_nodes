import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types.socket import AnimationNodeSocket
from .. utils.nodes import newNodeAtCursor, invokeTranslation

class BooleanSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_BooleanSocket"
    bl_label = "Boolean Socket"
    dataType = "Boolean"
    allowedInputTypes = ["Boolean"]
    drawColor = (0.7, 0.7, 0.4, 1)
    storable = True
    comparable = True

    value = BoolProperty(default = True, update = propertyChanged)
    showCreateCompareNodeButton = BoolProperty(default = False)

    def drawProperty(self, layout, text):
        row = layout.row()
        row.prop(self, "value", text = text)

        if self.showCreateCompareNodeButton and self.isUnlinked:
            self.invokeFunction(row, "createCompareNode", icon = "PLUS", emboss = False,
                description = "Create compare node")

    def getValue(self):
        return self.value

    def setProperty(self, data):
        self.value = data

    def getProperty(self):
        return self.value

    def createCompareNode(self):
        node = newNodeAtCursor("an_CompareNode")
        self.linkWith(node.outputs[0])
        invokeTranslation()


class BooleanListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_BooleanListSocket"
    bl_label = "Boolean List Socket"
    dataType = "Boolean List"
    baseDataType = "Boolean"
    allowedInputTypes = ["Boolean List"]
    drawColor = (0.7, 0.7, 0.4, 0.5)
    storable = True
    comparable = False

    def getValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"
