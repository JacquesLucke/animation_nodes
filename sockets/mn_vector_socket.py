import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *
from mathutils import Vector

class mn_VectorSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_VectorSocket"
    bl_label = "Vector Socket"
    dataType = "Vector"
    allowedInputTypes = ["Vector"]
    drawColor = (0.05, 0.05, 0.8, 0.7)
    
    vector = bpy.props.FloatVectorProperty(default = [0, 0, 0], update = nodePropertyChanged)
    
    def drawInput(self, layout, node, text):
        col = layout.column(align = True)
        col.label(text)
        col.prop(self, "vector", index = 0, text = "X")
        col.prop(self, "vector", index = 1, text = "Y")
        col.prop(self, "vector", index = 2, text = "Z")
        col.separator()
        
    def getValue(self):
        return Vector(self.vector)
        
    def setStoreableValue(self, data):
        self.vector = data
    def getStoreableValue(self):
        return self.vector[:]
        
    def getCopyValueFunctionString(self):
        return "return value.copy()"
