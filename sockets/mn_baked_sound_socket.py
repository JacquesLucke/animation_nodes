import bpy
from .. mn_execution import nodePropertyChanged
from .. mn_node_base import *
from .. utils.mn_node_utils import *

class mn_BakedSoundSocket(mn_BaseSocket, mn_SocketProperties):
    bl_idname = "mn_BakedSoundSocket"
    bl_label = "Baked Sound Socket"
    dataType = "Sound"
    allowedInputTypes = ["Sound"]
    drawColor = (0.5, 0.9, 0.6, 1)
        
    def getSoundBakeNodeItems(self, context):
        bakeNodeNames = getAttributesFromNodesWithType("mn_SoundBakeNode", "name")
        bakeNodeItems = []
        for name in bakeNodeNames:
            bakeNodeItems.append((name, name, ""))
        if len(bakeNodeItems) == 0: bakeNodeItems.append(("NONE", "NONE", ""))
        return bakeNodeItems
    
    bakeNodeName = bpy.props.EnumProperty(items = getSoundBakeNodeItems, name = "Bake Node", update = nodePropertyChanged)
    
    def drawInput(self, layout, node, text):
        if self.bakeNodeName == "NONE":
            newNode = layout.operator("node.add_node", text = "Sound Bake", icon = "PLUS")
            newNode.type = "mn_SoundBakeNode"
            newNode.use_transform = True
        else:
            layout.prop(self, "bakeNodeName", text = text)
        
    def getValue(self):
        return self.node.id_data.nodes.get(self.bakeNodeName)
        
    def setStoreableValue(self, data):
        self.bakeNodeName = data
    def getStoreableValue(self):
        return self.bakeNodeName
