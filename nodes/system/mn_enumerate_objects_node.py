import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_dynamic_sockets_helper import *

class mn_EnumerateObjectsNode(Node, AnimationNode):
	bl_idname = "mn_EnumerateObjectsNode"
	bl_label = "Loop Objects"
	
	def getStartLoopNames(self):
		nodeTree = self.id_data
		startLoopNames = []
		for node in nodeTree.nodes:
			if node.bl_idname == "mn_EnumerateObjectsStartNode": startLoopNames.append(node.loopName)
		return startLoopNames
	def getStartLoopNodeItems(self, context):
		startLoopNames = self.getStartLoopNames()
		startLoopItems = []
		for name in startLoopNames:
			startLoopItems.append((name, name, ""))
		if len(startLoopItems) == 0: startLoopItems.append(("NONE", "NONE", ""))
		return startLoopItems
	def selectedLoopStarterChanged(self, context):
		self.updateSockets(self.getStartNode())
	
	selectedLoop = bpy.props.EnumProperty(items = getStartLoopNodeItems, name = "Loop", update=selectedLoopStarterChanged)
	executeLoop = bpy.props.BoolProperty(name = "Execute Loop", default = True)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectListSocket", "Objects")
		self.outputs.new("mn_ObjectListSocket", "Objects")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		if self.selectedLoop == "NONE":
			newNode = layout.operator("node.add_node", text = "New Object Loop Start", icon = "PLUS")
			newNode.use_transform = True
			newNode.type = "mn_EnumerateObjectsStartNode"
		else:
			layout.prop(self, "selectedLoop")
		
		layout.prop(self, "executeLoop", text = "Execute Loop")
		
	def updateSockets(self, startNode, socketStartValue  = (None, None)):
		forbidCompiling()
		socketDescriptions = startNode.getSocketDescriptions()
		connections = getConnectionDictionaries(self)
		self.removeDynamicSockets()
		for customName, idName, identifier in socketDescriptions:
			inputSocket = self.inputs.new(idName, customName, identifier)
			if inputSocket.identifier == socketStartValue[0]:
				inputSocket.setStoreableValue(socketStartValue[1])
			self.outputs.new(idName, customName, identifier)
		tryToSetConnectionDictionaries(self, connections)
		allowCompiling()
		
	def removeDynamicSockets(self):
		for i, socket in enumerate(self.inputs):
			if i > 0: self.inputs.remove(socket)	
		for i, socket in enumerate(self.outputs):
			if i > 0: self.outputs.remove(socket)

	def getStartNode(self):
		selectedLoop = self.selectedLoop
		for node in self.id_data.nodes:
			if node.bl_idname == "mn_EnumerateObjectsStartNode":
				if node.loopName == selectedLoop:
					return node
		return None