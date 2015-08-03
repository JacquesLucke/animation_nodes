import bpy
from .. base_types.socket import AnimationNodeSocket

class EdgeIndicesSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_EdgeIndicesSocket"
    bl_label = "Edge Indices Socket"
    dataType = "Edge Indices"
    allowedInputTypes = ["Edge Indices"]
    drawColor = (1.0, 0.55, 0.23, 1)

    def drawInput(self, layout, node, text):
        layout.label(text)

    def getValue(self):
        return (0, 1)

    def getCopyValueFunctionString(self):
        return "return value[:]"
