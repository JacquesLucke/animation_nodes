import bpy
from bpy.props import *
from . mn_execution import nodeTreeChanged
from bpy.types import NodeTree, Node, NodeSocket
from . mn_utils import *

class mn_AnimationNodeTree(bpy.types.NodeTree):
    bl_idname = "mn_AnimationNodeTree"
    bl_label = "Animation";
    bl_icon = "ACTION"
    
    isAnimationNodeTree = bpy.props.BoolProperty(default = True)
    
    def update(self):
        nodeTreeChanged()
        
        
        
class AnimationNode:
    @classmethod
    def poll(cls, nodeTree):
        return nodeTree.bl_idname == "mn_AnimationNodeTree"
        

        
class mn_BaseSocket(NodeSocket):
    bl_idname = "mn_BaseSocket"
    bl_label = "Base Socket"
    
    def draw(self, context, layout, node, text):
        displayText = self.customName if self.displayCustomName else text
        if self.editableCustomName:
            row = layout.row(align = True)
            row.prop(self, "customName", text = "")
            if self.removeable:
                removeSocket = row.operator("mn.remove_socket", text = "", icon = "X")
                removeSocket.nodeTreeName = node.id_data.name
                removeSocket.nodeName = node.name
                removeSocket.isOutputSocket = self.is_output
                removeSocket.socketIdentifier = self.identifier
        else:
            row = layout.row()
            if not self.is_output and not isSocketLinked(self):
                self.drawInput(row, node, displayText)
            else:
                row.label(displayText)
            if self.removeable:
                removeSocket = row.operator("mn.remove_socket", text = "", icon = "X")
                removeSocket.nodeTreeName = node.id_data.name
                removeSocket.nodeName = node.name
                removeSocket.isOutputSocket = self.is_output
                removeSocket.socketIdentifier = self.identifier
            
    def draw_color(self, context, node):
        return self.drawColor
        
    def copySettingsFrom(self, node):
        self.setStoreableValue(node.getStoreableValue())
        attributes = [prop.identifier for prop in self.bl_rna.properties if not prop.is_readonly]
        for attribute in attributes:
            get = getattr(node, attribute, None)
            setattr(self, attribute, get)
        
        
def customNameChanged(self, context):
    if not self.customNameIsUpdating:
        self.customNameIsUpdating = True
        if self.customNameIsVariable:
            self.customName = makeVariableName(self.customName)
        if self.uniqueCustomName:
            customName = self.customName
            self.customName = "temporary name to avoid some errors"
            self.customName = getNotUsedCustomName(self.node, prefix = customName)
        if self.callNodeWhenCustomNameChanged:
            self.node.customSocketNameChanged(self)
        self.customNameIsUpdating = False
        nodeTreeChanged()
        
def makeVariableName(name):
    newName = ""
    for i, char in enumerate(name):
        if len(newName) == 0 and (char.isalpha() or char == "_"):
            newName += char
        elif len(newName) > 0 and (char.isalpha() or char.isnumeric() or char == "_"):
            newName += char
    return newName
    
def getNotUsedCustomName(node, prefix):
    customName = prefix
    while isCustomNameUsed(node, customName):
        customName = prefix + getRandomString(3)
    return customName
    
def isCustomNameUsed(node, name):
    for socket in node.inputs:
        if socket.customName == name: return True
    for socket in node.outputs:
        if socket.customName == name: return True
    return False
    
    
def getSocketVisibility(socket):
    return not socket.hide
def setSocketVisibility(socket, value):
    socket.hide = not value
    
bpy.types.NodeSocket.show = BoolProperty(default = True, get = getSocketVisibility, set = setSocketVisibility)    
    
class mn_SocketProperties:
    editableCustomName = BoolProperty(default = False)
    customName = StringProperty(default = "custom name", update = customNameChanged)
    displayCustomName = BoolProperty(default = False)
    uniqueCustomName = BoolProperty(default = True)
    customNameIsVariable = BoolProperty(default = False)
    customNameIsUpdating = BoolProperty(default = False)
    removeable = BoolProperty(default = False)
    callNodeToRemove = BoolProperty(default = False)
    callNodeWhenCustomNameChanged = BoolProperty(default = False)
    loopAsList = BoolProperty(default = False)
       
        
class RemoveSocketOperator(bpy.types.Operator):
    bl_idname = "mn.remove_socket"
    bl_label = "Remove Socket"
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    isOutputSocket = bpy.props.BoolProperty()
    socketIdentifier = bpy.props.StringProperty()
    
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        socket = getSocketByIdentifier(node, self.isOutputSocket, self.socketIdentifier)
        if socket.callNodeToRemove:
            node.removeSocket(socket)
        else:
            if self.isOutputSocket: node.outputs.remove(socket)
            else: node.inputs.remove(socket)
        return {'FINISHED'}
