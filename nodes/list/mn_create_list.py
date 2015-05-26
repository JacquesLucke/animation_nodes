import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

def getListTypeItems(self, context):
    listTypeItems = []
    for idName in getListSocketIdNames():
        baseIdName = getListBaseSocketIdName(idName)
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
        self.callFunctionFromUI(layout, "newInputSocket",
            text = "New Input",
            description = "Create a new input socket",
            icon = "PLUS")
        layout.prop(self, "manageSockets")
        
    def draw_buttons_ext(self, context, layout):
        col = layout.column(align = True)
        col.prop(self, "selectedListType", text = "")
        self.callFunctionFromUI(col, "assignSelectedListType", 
            text = "Assign", 
            description = "Remove all sockets and set the selected socket type")
        
    def execute(self, inputs):
        elements = []
        for socket in self.inputs:
            elements.append(inputs[socket.identifier])
        return {"List" : elements}
        
    def assignSelectedListType(self):
        self.assignListType(self.selectedListType)
        
    def assignListType(self, idName, inputAmount = 2):
        self.listType = idName
        self.recreateSockets(inputAmount)
        
    def recreateSockets(self, inputAmount = 2):
        forbidCompiling()
        self.inputs.clear()
        self.outputs.clear()
        
        for i in range(inputAmount):
            self.newInputSocket()
        self.outputs.new(self.listType, "List")
        allowCompiling()
        nodeTreeChanged()
        
    def newInputSocket(self):
        baseIdName = getListBaseSocketIdName(self.listType)
        socket = self.inputs.new(baseIdName, getNotUsedSocketName(self, "Element"))
        socket.displayCustomName = True
        socket.uniqueCustomName = False
        socket.customName = "Element"
        socket.removeable = self.manageSockets
        socket.moveable = self.manageSockets
        if hasattr(socket, "showName"):
            socket.showName = False             