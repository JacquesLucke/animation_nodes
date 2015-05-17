import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

def getListTypeItems(self, context):
    listTypeItems = []
    for idName in getListDataTypes():
        baseIdName = getBaseSocketType(idName)
        cls = getSocketClassFromIdName(baseIdName)
        item = (idName, cls.dataType, "")
        listTypeItems.append(item)
    return listTypeItems

class mn_CreateList(Node, AnimationNode):
    bl_idname = "mn_CreateList"
    bl_label = "Create List"
    
    selectedListType = EnumProperty(name = "List Type", items = getListTypeItems)
    listType = StringProperty(default = "mn_FloatListSocket")
    
    def init(self, context):
        forbidCompiling()
        self.recreateSockets()
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        props = layout.operator("mn.append_socket_to_list_create_node", text = "New Input", icon = "PLUS")
        props.nodeTreeName = self.id_data.name
        props.nodeName = self.name
        
    def draw_buttons_ext(self, context, layout):
        col = layout.column(align = True)
        col.prop(self, "selectedListType", text = "")
        props = col.operator("mn.assign_selected_type_to_list_create_node", text = "Assign")
        props.nodeTreeName = self.id_data.name
        props.nodeName = self.name
        
    def execute(self, inputs):
        elements = []
        for socket in self.inputs:
            elements.append(inputs[socket.identifier])
        return {"List" : elements}
        
    def assignListType(self, idName):
        self.listType = idName
        self.recreateSockets()
        
    def recreateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        
        self.newInputSocket()
        self.newInputSocket()
        self.newInputSocket()
        self.newInputSocket()
        self.outputs.new(self.listType, "List")
        
    def newInputSocket(self):
        baseIdName = getBaseSocketType(self.listType)
        socket = self.inputs.new(baseIdName, getNotUsedSocketName(self, "Element"))
        socket.displayCustomName = True
        socket.uniqueCustomName = False
        socket.customName = "Element"
        socket.removeable = True
        if hasattr(socket, "showName"):
            socket.showName = False
        
        
class AssignListType(bpy.types.Operator):
    bl_idname = "mn.assign_selected_type_to_list_create_node"
    bl_label = "Assign List Type"
    bl_description = "Remove all sockets and set the selected socket type"
    bl_options = {"REGISTER"}
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.assignListType(node.selectedListType)
        return {"FINISHED"}
                
                
class AppendSocket(bpy.types.Operator):
    bl_idname = "mn.append_socket_to_list_create_node"
    bl_label = "Append Socket"
    bl_description = "Create a new input socket"
    bl_options = {"REGISTER"}
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        node.newInputSocket()
        return {"FINISHED"}                