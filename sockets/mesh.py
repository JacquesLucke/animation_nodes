import bpy, bmesh
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_MeshSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_MeshSocket"
    bl_label = "Mesh Socket"
    dataType = "Mesh"
    allowedInputTypes = ["Mesh"]
    drawColor = (0.1, 1.0, 0.1, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return bmesh.new()
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass
        
    def getCopyValueFunctionString(self):
        return "return value.copy()"
