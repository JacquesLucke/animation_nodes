import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *

newOutputSocketName = "New Output"

class mn_GroupOutput(bpy.types.Node, AnimationNode):
    bl_idname = "mn_GroupOutput"
    bl_label = "Group Output"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_EmptySocket", newOutputSocketName)
        allowCompiling()
        
    def execute(self, input):
        return input
        
    def update(self):
        forbidCompiling()
        socket = self.inputs.get(newOutputSocketName)
        fromSocket = self.getValidFromSocketAndRemoveLink(socket)
        if fromSocket is not None:
            socketType = fromSocket.bl_idname
            newSocket = self.newInputSocket(socketType, namePrefix = fromSocket.name)
            self.id_data.links.new(newSocket, fromSocket)
            newIndex = self.inputs.find(socket.name)
            self.inputs.move(len(self.inputs) - 1, newIndex)
            self.updateCallerNodes()
        else:
            removeLinksFromSocket(socket)
        allowCompiling()
    
    def getValidFromSocketAndRemoveLink(self, socket):
        if socket is None:
            return None
        links = socket.links
        if len(links) == 0:
            return None
        fromSocket = links[0].from_socket
        self.id_data.links.remove(links[0])
        if fromSocket.node.type == "REROUTE":
            return None
        if fromSocket.bl_idname == "mn_EmptySocket":
            return None
        return fromSocket
        
    def newInputSocket(self, idName, namePrefix):
        socket = self.inputs.new(idName, getNotUsedSocketName(self, prefix = "socket"))
        socket.customName = getNotUsedCustomSocketName(self, prefix = namePrefix)
        socket.editableCustomName = True
        socket.callNodeWhenCustomNameChanged = True
        socket.removeable = True
        socket.callNodeToRemove = True
        return socket
        
    def removeSocket(self, socket):
        self.inputs.remove(socket)
        self.updateCallerNodes()
        
    def free(self):
        self.updateCallerNodes(outputRemoved = True)
        
    def customSocketNameChanged(self, socket):
        self.updateCallerNodes()
        
    def updateCallerNodes(self, outputRemoved = False):
        network = NodeNetwork.fromNode(self)
        inputNode = network.getGroupInputNode()
        if inputNode is not None:
            inputNode.updateCallerNodes(outputRemoved = outputRemoved)
        
    def getSockets(self):
        sockets = []
        for socket in self.inputs:
            if socket.name != newOutputSocketName:
                sockets.append(socket)
        return sockets