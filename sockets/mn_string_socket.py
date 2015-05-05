import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_StringSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_StringSocket"
    bl_label = "String Socket"
    dataType = "String"
    allowedInputTypes = ["String"]
    drawColor = (1, 1, 1, 1)
    
    string = bpy.props.StringProperty(default = "", update = nodePropertyChanged, options = {"TEXTEDIT_UPDATE"})
    showName = bpy.props.BoolProperty(default = True)
    
    def drawInput(self, layout, node, text):
        if not self.showName: text = ""
        layout.prop(self, "string", text = text)
        
    def getValue(self):
        return self.string
        
    def setStoreableValue(self, data):
        self.string = data
    def getStoreableValue(self):
        return self.string
