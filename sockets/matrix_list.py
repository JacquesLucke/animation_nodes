import bpy
from .. mn_node_base import *

class mn_MatrixListSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_MatrixListSocket"
    bl_label = "Matrix List Socket"
    dataType = "Matrix List"
    allowedInputTypes = ["Matrix List"]
    drawColor = (1, 0.7, 0.2, 1)

    def drawInput(self, layout, node, text):
        layout.label(text)

    def getValue(self):
        return []

    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        return []

    def getCopyValueFunctionString(self):
        return "return [element.copy() for element in value]"
