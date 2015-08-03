import bpy
from .. mn_execution import nodePropertyChanged
from .. base_types.socket import AnimationNodeSocket
from mathutils import Vector

class mn_VectorSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_VectorSocket"
    bl_label = "Vector Socket"
    dataType = "Vector"
    allowedInputTypes = ["Vector"]
    drawColor = (0.05, 0.05, 0.8, 0.7)
    
    value = bpy.props.FloatVectorProperty(default = [0, 0, 0], update = nodePropertyChanged)
    showName = bpy.props.BoolProperty(default = True)
    
    def drawInput(self, layout, node, text):
        col = layout.column(align = True)
        if self.showName: col.label(text)
        col.prop(self, "value", index = 0, text = "X")
        col.prop(self, "value", index = 1, text = "Y")
        col.prop(self, "value", index = 2, text = "Z")
        col.separator()
        
    def getValue(self):
        return Vector(self.value)
        
    def setStoreableValue(self, data):
        self.value = data
    def getStoreableValue(self):
        return self.value[:]
        
    def getCopyValueFunctionString(self):
        return "return value.copy()"
