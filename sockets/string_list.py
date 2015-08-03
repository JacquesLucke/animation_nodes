import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_StringListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_StringListSocket"
    bl_label = "String List Socket"
    dataType = "String List"
    allowedInputTypes = ["String List"]
    drawColor = (1, 1, 1, 0.4)
    recreateValueOnEachUse = True
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return []
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        return []
        
    def getCopyValueFunctionString(self):
        return "return value[:]"
