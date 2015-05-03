import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.utils.mn_node_utils import *
from animation_nodes.sockets.mn_socket_info import *

newInputSocketName = "New Input"

class mn_GroupInput(Node, AnimationNode):
    bl_idname = "mn_GroupInput"
    bl_label = "Group Input"
    
    def groupNameChanged(self, context):
        if not self.nameIsChanging:
            self.nameIsChanging = True
            self.groupName = self.getNotUsedGroupName(prefix = self.groupName)
            self.nameIsChanging = False
    
    groupName = bpy.props.StringProperty(default = "Group", update = groupNameChanged)
    nameIsChanging = bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        forbidCompiling()
        self.groupName = self.getNotUsedGroupName()
        self.outputs.new("mn_EmptySocket", newInputSocketName)
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        row = layout.row(align = True)
        
    def execute(self, input):
        return input
        
    def draw_buttons(self, context, layout):
        row = layout.row(align = True)
        row.prop(self, "groupName", text = "")
        
    def update(self):
        forbidCompiling()
        socket = self.outputs.get(newInputSocketName)
        targetSocket = self.getValidTargetSocket(socket)
        if targetSocket is not None:
            socketType = self.getTargetSocketType(targetSocket)
            newSocket = self.newOutputSocket(socketType, namePrefix = targetSocket.name)
            self.id_data.links.new(targetSocket, newSocket)
            newIndex = self.outputs.find(socket.name)
            self.outputs.move(len(self.outputs) - 1, newIndex)
            self.updateCallerNodes((newSocket, targetSocket.getStoreableValue()))
        else:
            removeLinksFromSocket(socket)
        allowCompiling()
    
    def getValidTargetSocket(self, socket):
        if socket is None:
            return None
        links = socket.links
        if len(links) == 0:
            return None
        toSocket = links[0].to_socket
        if toSocket.node.type == "REROUTE":
            return None
        if getattr(toSocket, "passiveSocketType", "other node") == "":
            return None
        return toSocket
        
    def getTargetSocketType(self, targetSocket):
        idName = targetSocket.bl_idname
        if idName == "mn_EmptySocket":
            if targetSocket.passiveSocketType != "":
                idName = targetSocket.passiveSocketType
        return idName
        
    def newOutputSocket(self, idName, namePrefix):
        socket = self.outputs.new(idName, getNotUsedSocketName(self, prefix = "socket"))
        socket.customName = getNotUsedCustomSocketName(self, prefix = namePrefix)
        targetSocket = None
        socket.editableCustomName = True
        socket.callNodeWhenCustomNameChanged = True
        socket.removeable = True
        socket.callNodeToRemove = True
        return socket
        
    def removeSocket(self, socket):
        self.outputs.remove(socket)
        self.updateCallerNodes()
        
    def customSocketNameChanged(self, socket):
        self.updateCallerNodes()
        
    def updateCallerNodes(self, socketStartValue = (None, None), inputRemoved = False, outputRemoved = False):
        nodes = getNodesFromTypeWithAttribute("mn_GroupCaller", "activeGroup", self.groupName)
        for node in nodes:
            node.updateSockets(socketStartValue, inputRemoved = inputRemoved, outputRemoved = outputRemoved)
        
    def getNotUsedGroupName(self, prefix = "Group"):
        groupName = prefix
        while getNodeFromTypeWithAttribute("mn_GroupInput", "groupName", groupName) not in [self, None]:
            groupName = prefix + getRandomString(3)
        return groupName
        
    def copy(self, node):
        self.groupName = self.getNotUsedGroupName()
        
    isRemoved = bpy.props.BoolProperty(default = False)
    def free(self):
        self.isRemoved = True
        self.updateCallerNodes(inputRemoved = True)

    def getSockets(self):
        sockets = []
        for socket in self.outputs:
            if socket.name != newInputSocketName:
                sockets.append(socket)
        return sockets
            