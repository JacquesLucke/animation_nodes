import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... utils.mn_node_utils import *
from ... utils.selection import getSortedSelectedObjectNames
from ... sockets.mn_socket_info import *
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
    #heavy copy from create list, comments in comparison to that, except execute..
def getListTypeItems(self, context):
    listTypeItems = []
    for idName in getListSocketIdNames():
        baseIdName = getListBaseSocketIdName(idName)
        cls = getSocketClassFromIdName(baseIdName)
        item = (idName, cls.dataType, "")
        listTypeItems.append(item)
    return listTypeItems
    
class mn_CombineListsNode(Node, AnimationNode):
    bl_idname = "mn_CombineListsNode"
    bl_label = "Combine Lists"
    
    def settingChanged(self, context):
        for socket in self.inputs:
            socket.moveable = self.manageSockets
            socket.removeable = self.manageSockets
            socket.hide = self.hideInputs
    
    selectedListType = EnumProperty(name = "List Type", items = getListTypeItems)
    listType = StringProperty(default = "mn_ObjectListSocket")
    manageSockets = BoolProperty(name = "Manage Sockets", default = False, description = "Allows to (re)move the input sockets", update = settingChanged)
    
    hideInputs = BoolProperty(name = "Hide Inputs", default = False, update = settingChanged)
    
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
            
        layout.prop(self, "hideInputs")
        #no drawTypeSpecificButtonsExt needed for list inputs
        
    def execute(self, inputs):  #should I try inline? hmm
        inputLists = []
        for socket in self.inputs:
            inputLists.append(inputs[socket.identifier])
        list = []
        for el in inputLists:
            list.extend(el)

        return {"List" : list}
        
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
        socket = self.inputs.new(self.listType, getNotUsedSocketName(self, "List"))#suffices for list type soc
        socket.displayCustomName = True
        socket.uniqueCustomName = False
        socket.customName = "List"
        socket.removeable = self.manageSockets
        socket.moveable = self.manageSockets
        # showName not the case on list sockets
        return socket
        
        #no drawTypeSpecificButtonsExt needed for list inputs
