import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *

loopTypes = [
    ("Generic", "NONE"),
    ("Object", "OBJECT"),
    ("Polygon", "POLYGON"),
    ("Vertex", "VERTEX"),
    ("Vector List", "VECTOR_LIST") ]

class mn_LoopCallerNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_LoopCallerNode"
    bl_label = "Loop Call"
    
    def getStartLoopNodeItems(self, context):
        startLoopNames = getAttributesFromNodesWithType("mn_LoopStartNode", "loopName")
        
        startLoopItems = []
        for loopName in startLoopNames:
            startLoopItems.append((loopName, loopName, ""))

        if len(startLoopItems) == 0:
            startLoopItems.append(("NONE", "NONE", ""))
        return startLoopItems
    
    def updateActiveL(self, context):
        self.updateActiveLoop()

    selectedLoop = bpy.props.EnumProperty(
        items=getStartLoopNodeItems,
        name="Selected Loop",
        update=updateActiveL)
    activeLoop = bpy.props.StringProperty(name = "Active Loop", default = "Loop")
    
    def init(self, context):
        forbidCompiling()
        self.updateActiveLoop()
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        col = layout.column(align = True)
        col.operator("wm.call_menu", text = "New Loop").name = "mn.add_loop_node_menu"
        row = col.row(align = True)
        row.prop(self, "selectedLoop", text = "")
        self.callFunctionFromUI(row, "updateActiveLoop", text = "", icon = "FILE_REFRESH")
        layout.label("Active: \"" + self.activeLoop + "\"")
        
        if self.getStartNode() is None:
            layout.label("Cannot find Loop", icon = "ERROR")
        
    def updateSockets(self, socketStartValue = (None, None)):
        forbidCompiling()
        startNode = self.getStartNode()
        if startNode is None:
            self.resetSockets()
        else:
            connections = getConnectionDictionaries(self)
            self.resetSockets()
            fromListSockets, fromSingleSockets = startNode.getSocketDescriptions()
            
            self.inputs["Amount"].hide = len(fromListSockets) != 0
            
            for socket in fromListSockets:
                idName = self.getSocketTypeForListSocket(socket.bl_idname)
                self.inputs.new(idName, socket.customName + " List", socket.identifier + "list")
                self.outputs.new(idName, socket.customName + " List", socket.identifier + "list")
                
            for socket in fromSingleSockets:
                inputSocket = self.inputs.new(socket.bl_idname, socket.customName, socket.identifier)
                if socket == socketStartValue[0]:
                    inputSocket.setStoreableValue(socketStartValue[1])
                self.outputs.new(socket.bl_idname, socket.customName, socket.identifier)
                
            tryToSetConnectionDictionaries(self, connections)
        allowCompiling()
        
    def loopRemoved(self):
        self.resetSockets()
        self.inputs["Amount"].hide = True
        
    def resetSockets(self):
        forbidCompiling()
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new("mn_IntegerSocket", "Amount")
        allowCompiling()
            
    def getSocketTypeForListSocket(self, socketType):
        listSocketType = getListSocketIdName(socketType)
        if listSocketType == None: return "mn_GenericSocket"
        return listSocketType

    def getStartNode(self):
        return getNodeFromTypeWithAttribute("mn_LoopStartNode", "loopName", self.activeLoop)
        
    def updateActiveLoop(self):
        if self.selectedLoop != "NONE":
            self.activeLoop = self.selectedLoop
        self.updateSockets()
        nodeTreeChanged()

        
class AddLoopNodeMenu(bpy.types.Menu):
    bl_idname = "mn.add_loop_node_menu"
    bl_label = "New Loop"
    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        for loopType in loopTypes:
            newNode = layout.operator("node.add_node", text = loopType[0])
            newNode.use_transform = True
            newNode.type = "mn_LoopStartNode"
            setting = newNode.settings.add()
            setting.name = "preset"
            setting.value = repr(loopType[1])