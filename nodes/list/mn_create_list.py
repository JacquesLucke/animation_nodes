import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

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
    
    def settingChanged(self, context):
        for socket in self.inputs:
            socket.moveable = self.manageSockets
            socket.removeable = self.manageSockets
    
    selectedListType = EnumProperty(name = "List Type", items = getListTypeItems)
    listType = StringProperty(default = "mn_FloatListSocket")
    manageSockets = BoolProperty(name = "Manage Sockets", default = False, description = "Allows to (re)move the input sockets", update = settingChanged)
    
    def init(self, context):
        forbidCompiling()
        self.recreateSockets()
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        props = layout.operator("mn.append_socket_to_list_create_node", text = "New Input", icon = "PLUS")
        props.nodeTreeName = self.id_data.name
        props.nodeName = self.name
        layout.prop(self, "manageSockets")
        
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
        forbidCompiling()
        self.inputs.clear()
        self.outputs.clear()
        
        self.newInputSocket()
        self.newInputSocket()
        self.outputs.new(self.listType, "List")
        allowCompiling()
        nodeTreeChanged()
        
    def newInputSocket(self):
        baseIdName = getBaseSocketType(self.listType)
        socket = self.inputs.new(baseIdName, getNotUsedSocketName(self, "Element"))
        socket.displayCustomName = True
        socket.uniqueCustomName = False
        socket.customName = "Element"
        socket.removeable = self.manageSockets
        socket.moveable = self.manageSockets
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