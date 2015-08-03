import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket
from .. data_structures.mesh import MeshData

class mn_MeshDataSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_MeshDataSocket"
    bl_label = "Mesh Data Socket"
    dataType = "Mesh Data"
    allowedInputTypes = ["Mesh Data"]
    drawColor = (0.3, 0.4, 0.18, 1)
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return MeshData([], [], [])
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        pass

    def getCopyValueFunctionString(self):
        return "return value.copy()"