import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_PolygonIndicesSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_PolygonIndicesSocket"
    bl_label = "Polygon Indices Socket"
    dataType = "Polygon Indices"
    allowedInputTypes = ["Polygon Indices"]
    drawColor = (0.5, 0.8, 0.4, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return (0, 1, 2)
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass

    def getCopyValueFunctionString(self):
        return "return value[:]"