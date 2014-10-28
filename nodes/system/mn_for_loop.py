import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_node_utils import *
from mn_socket_info import *

class mn_ForLoopNode(Node, AnimationNode):
	bl_idname = "mn_ForLoopNode"
	bl_label = "For Loop"
	
	def getStartLoopNodeItems(self, context):
		startLoopNodes = getNodesFromType("mn_ForLoopStartNode")
		startLoopItems = []
		for node in startLoopNodes:
			startLoopItems.append((node.loopName, node.loopName, ""))
		if len(startLoopItems) == 0: startLoopItems.append(("NONE", "NONE", ""))
		return startLoopItems
	def selectedLoopStarterChanged(self, context):
		self.updateSockets(self.getStartNode())
	
	selectedLoop = bpy.props.EnumProperty(items = getStartLoopNodeItems, name = "Loop", update=selectedLoopStarterChanged)
	executeLoop = bpy.props.BoolProperty(name = "Execute Loop", default = True)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Amount")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		if self.selectedLoop == "NONE":
			newNode = layout.operator("node.add_node", text = "New Loop Start", icon = "PLUS")
			newNode.use_transform = True
			newNode.type = "mn_ForLoopStartNode"
		else:
			layout.prop(self, "selectedLoop")
		
		layout.prop(self, "executeLoop", text = "Execute Loop")
		
	def updateSockets(self, startNode):
		forbidCompiling()
		connections = getConnectionDictionaries(self)
		self.removeSockets()
		fromListSockets, fromSingleSockets = startNode.getSocketDescriptions()
		
		for socket in fromListSockets:
			idName = self.getSocketTypeForListSocket(socket.bl_idname)
			self.inputs.new(idName, socket.customName, socket.identifier + "list")
			self.outputs.new(idName, socket.customName, socket.identifier + "list")
			
		for socket in fromSingleSockets:
			self.inputs.new(socket.bl_idname, socket.customName, socket.identifier)
			self.outputs.new(socket.bl_idname, socket.customName, socket.identifier)
			
		tryToSetConnectionDictionaries(self, connections)
		allowCompiling()
		
	def removeSockets(self):
		self.outputs.clear()
		for i, socket in enumerate(self.inputs):
			if i > 0: self.inputs.remove(socket)
			
	def getSocketTypeForListSocket(self, socketType):
		listSocketType = getListSocketType(socketType)
		if listSocketType == None: return "mn_GenericSocket"
		return listSocketType

	def getStartNode(self):
		return getNodeFromTypeWithAttribute("mn_ForLoopStartNode", "loopName", self.selectedLoop)