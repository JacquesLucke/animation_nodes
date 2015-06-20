import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *

newListSocketName = "New List"
newOptionSocketName = "New Option"

presets = {
    "OBJECT" : ([("mn_ObjectSocket", "Object")], []),
    "POLYGON" : ([("mn_PolygonSocket", "Polygon")], []),
    "VERTEX" : ([("mn_VertexSocket", "Vertex")], []),
    "VECTOR_LIST" : ([("mn_VectorSocket", "Source")], [("mn_VectorListSocket", "New List")]) }

class mn_LoopStartNode(Node, AnimationNode):
    bl_idname = "mn_LoopStartNode"
    bl_label = "Loop Start"
    
    def loopNameChanged(self, context):
        if not self.nameIsChanging:
            self.nameIsChanging = True
            self.loopName = self.getNotUsedLoopName(prefix = self.loopName)
            self.nameIsChanging = False
            nodeTreeChanged()
    def presetChanged(self, context):
        self.buildPreset()
    
    loopName = bpy.props.StringProperty(default = "Object Loop", update = loopNameChanged)
    nameIsChanging = bpy.props.BoolProperty(default = False)
    preset = bpy.props.StringProperty(default = "", update = presetChanged)
    selectedSocketType = bpy.props.EnumProperty(name = "Selected Socket Type", items = getSocketDataTypeItems, description = "Choose the type that the loop starter node will have")
    
    def init(self, context):
        forbidCompiling()
        self.loopName = self.getNotUsedLoopName()
        self.outputs.new("mn_IntegerSocket", "Index")
        self.outputs.new("mn_IntegerSocket", "List Length")
        self.outputs.new("mn_EmptySocket", newListSocketName)
        self.outputs.new("mn_EmptySocket", newOptionSocketName)
        self.updateCallerNodes()
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        row = layout.row(align = True)
    
        row.prop(self, "loopName", text = "")
        
        newNode = row.operator("node.add_node", text = "", icon = "PLUS")
        newNode.use_transform = True
        newNode.type = "mn_LoopCallerNode"
        setting = newNode.settings.add()
        setting.name = "activeLoop"
        setting.value = repr(self.loopName)
        
    def draw_buttons_ext(self, context, layout):
        col = layout.column(align = True)
        col.label("New Socket")
        col.prop(self, "selectedSocketType", text = "")
        
        row = col.row(align = True)
        
        operator = row.operator("mn.append_socket_to_loop_node", text = "List")
        operator.nodeTreeName = self.id_data.name
        operator.nodeName = self.name
        operator.isListSocket = True
        
        operator = row.operator("mn.append_socket_to_loop_node", text = "Option")
        operator.nodeTreeName = self.id_data.name
        operator.nodeName = self.name
        operator.isListSocket = False
        
    def execute(self, input):
        return input
        
    def update(self):
        forbidCompiling()
        
        # from list socket
        socket = self.outputs.get(newListSocketName)
        targetSocket = self.getValidTargetSocket(socket)
        if targetSocket is not None:
            socketType = self.getTargetSocketType(targetSocket)
            if hasListSocket(socketType):
                newSocket = self.newOutputSocket(socketType, namePrefix = targetSocket.name)
                newSocket.loopAsList = True
                self.id_data.links.new(targetSocket, newSocket)
                newIndex = self.outputs.find(socket.name)
                self.outputs.move(len(self.outputs) - 1, newIndex)
                self.updateCallerNodes()
            else:
                self.id_data.links.remove(socket.links[0])
        else:
            removeLinksFromSocket(socket)
            
        # from single socket
        socket = self.outputs.get(newOptionSocketName)
        targetSocket = self.getValidTargetSocket(socket)
        if targetSocket is not None:
            socketType = self.getTargetSocketType(targetSocket)
            newSocket = self.newOutputSocket(socketType, namePrefix = targetSocket.name)
            self.id_data.links.new(targetSocket, newSocket)
            newIndex = self.outputs.find(socket.name)
            self.outputs.move(len(self.outputs) - 1, newIndex)
            socketStartValue = (None, None)
            if targetSocket.bl_idname != "mn_EmptySocket":
                socketStartValue = (newSocket, targetSocket.getStoreableValue())
            self.updateCallerNodes(socketStartValue)
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
        
    def updateCallerNodes(self, socketStartValue = (None, None)):
        nodes = getNodesFromTypeWithAttribute("mn_LoopCallerNode", "activeLoop", self.loopName)
        for node in nodes:
            node.updateSockets(socketStartValue)
        nodeTreeChanged()
        
    def clearCallerNodes(self):
        nodes = getNodesFromTypeWithAttribute("mn_LoopCallerNode", "activeLoop", self.loopName)
        for node in nodes:
            node.loopRemoved()
            
    def getSocketDescriptions(self):
        fromListSockets = []
        fromSingleSockets = []
        
        for i, socket in enumerate(self.outputs):
            if i > 1 and socket.bl_idname != "mn_EmptySocket":
                if socket.loopAsList: fromListSockets.append(socket)
                else: fromSingleSockets.append(socket)
            
        return (fromListSockets, fromSingleSockets)
        
    def getNotUsedLoopName(self, prefix = "Loop"):
        loopName = prefix
        while getNodeFromTypeWithAttribute("mn_LoopStartNode", "loopName", loopName) not in [self, None]:
            loopName = prefix + getRandomString(3)
        return loopName
        
    def buildPreset(self):
        forbidCompiling()
        self.outputs.clear()
        preset = presets.get(self.preset)
        self.outputs.new("mn_IntegerSocket", "Index")
        self.outputs.new("mn_IntegerSocket", "List Length")
        if preset is not None:
            for idName, customName in preset[0]:
                socket = self.newOutputSocket(idName, namePrefix = customName)
                socket.loopAsList = True
        self.outputs.new("mn_EmptySocket", newListSocketName)
        if preset is not None:
            for idName, customName in preset[1]:
                socket = self.newOutputSocket(idName, namePrefix = customName)
        self.outputs.new("mn_EmptySocket", newOptionSocketName)
        self.updateCallerNodes()
        allowCompiling()
            
    def removeDynamicSockets(self):
        for socket in self.outputs:
            if socket.identifier not in ["Index", "List Length", newListSocketName, newOptionSocketName]:
                self.outputs.remove(socket)
                
    def customSocketNameChanged(self, socket):
        self.updateCallerNodes()
        
    def removeSocket(self, socket):
        self.outputs.remove(socket)
        self.updateCallerNodes()
    
    def copy(self, node):
        self.loopName = self.getNotUsedLoopName()
        
    def free(self):
        self.clearCallerNodes()

        
class AppendSocket(bpy.types.Operator):
    bl_idname = "mn.append_socket_to_loop_node"
    bl_label = "Append Socket to Loop Node"
    bl_description = "Append a new socket to this loop"
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
    isListSocket = bpy.props.BoolProperty()

    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        type = getIdNameFromDataType(node.selectedSocketType)
        newSocket = node.newOutputSocket(type, "socket")
        if self.isListSocket:
            newSocket.loopAsList = True
            index = node.outputs.find(newListSocketName)
        else:
            index = node.outputs.find(newOptionSocketName)
        node.outputs.move(len(node.outputs)-1, index)
        node.updateCallerNodes()
        return {'FINISHED'}        