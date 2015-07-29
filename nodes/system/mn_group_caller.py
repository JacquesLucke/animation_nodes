import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *

newOutputSocketName = "New Output"

class mn_GroupCaller(bpy.types.Node, AnimationNode):
    bl_idname = "mn_GroupCaller"
    bl_label = "Group Call"
    
    def getNodeGroupItems(self, context):
        nodes = getNodesFromType("mn_GroupInput")
        groupItems = []
        for node in nodes:
            groupItems.append((node.groupName, node.groupName, ""))
        if len(groupItems) == 0: groupItems.append(("NONE", "NONE", ""))
        return groupItems
    
    selectedGroup = bpy.props.EnumProperty(items = getNodeGroupItems, name = "Selected Group")
    activeGroup = bpy.props.StringProperty(default = "")
    
    def init(self, context):
        forbidCompiling()
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        row = layout.row(align = True)
        row.prop(self, "selectedGroup", text = "")
        self.callFunctionFromUI(row, "updateActiveGroup", text = "", icon = "FILE_REFRESH")
        layout.label("Group: " + self.activeGroup)
        
    def updateSockets(self, socketStartValue = (None, None), inputRemoved = False, outputRemoved = False):
        forbidCompiling()
        connections = getConnectionDictionaries(self)
        self.removeSockets()
        
        inputNode = getNodeFromTypeWithAttribute("mn_GroupInput", "groupName", self.activeGroup)
        if inputNode is not None and not inputRemoved:
            network = NodeNetwork.fromNode(inputNode)
            if network.type == "Group":
                for socket in inputNode.getSockets():
                    newSocket = self.inputs.new(socket.bl_idname, socket.customName, socket.identifier)
                    if socket == socketStartValue[0]: newSocket.setStoreableValue(socketStartValue[1])
                if not outputRemoved:
                    outputNode = network.getGroupOutputNode()
                    if outputNode is not None:
                        for socket in outputNode.getSockets():
                            newSocket = self.outputs.new(socket.bl_idname, socket.customName, socket.identifier)
                            if socket == socketStartValue[0]: newSocket.setStoreableValue(socketStartValue[1])
        
        tryToSetConnectionDictionaries(self, connections)
        allowCompiling()
        nodeTreeChanged()
        
    def removeSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        
    def updateActiveGroup(self):
        self.activeGroup = self.selectedGroup
        self.updateSockets()
        
    def getInputNode(self):
        return getNodeFromTypeWithAttribute("mn_GroupInput", "groupName", self.activeGroup)