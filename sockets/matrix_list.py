import bpy
from .. base_types.socket import AnimationNodeSocket

class mn_MatrixListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
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
