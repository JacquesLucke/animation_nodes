import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket

class mn_EmptySocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_EmptySocket"
    bl_label = "Empty Socket"
    dataType = "Empty"
    allowedInputTypes = ["all"]
    drawColor = (0.0, 0.0, 0.0, 0.0)
    
    passiveSocketType = bpy.props.StringProperty(default = "")
    
    def drawInput(self, layout, node, text):
        layout.label(text)
        
    def getValue(self):
        return None
        
    def setStoreableValue(self, data):
        pass
    def getStoreableValue(self):
        return None
