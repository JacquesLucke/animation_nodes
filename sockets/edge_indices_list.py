import bpy
from .. base_types.socket import AnimationNodeSocket

class EdgeIndicesListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_EdgeIndicesListSocket"
    bl_label = "Edge Indices List Socket"
    dataType = "Edge Indices List"
    allowedInputTypes = ["Edge Indices List"]
    drawColor = (0, 0.55, 0.23, 1)

    def drawInput(self, layout, node, text):
        layout.label(text)

    def getValue(self):
        return []

    def setStoreableValue(self, data):
        pass
        
    def getStoreableValue(self):
        pass

    def getCopyValueFunctionString(self):
        return "return [edgeIndices[:] for edgeIndices in value]"
