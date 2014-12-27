import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.utils.mn_node_utils import *
from animation_nodes.sockets.mn_socket_info import *

loopTypes = [("Generic", "NONE"), ("Object", "OBJECT"), ("Polygon", "POLYGON"), ("Vertex", "VERTEX")]

class mn_LoopCallerNode(Node, AnimationNode):
	bl_idname = "mn_LoopCallerNode"
	bl_label = "Loop Call"
	
	def getStartLoopNodeItems(self, context):
		startLoopNames = getAttributesFromNodesWithType("mn_LoopStartNode", "loopName")
		startLoopNames.sort()
		startLoopNames.reverse()
		startLoopItems = []
		for loopName in startLoopNames:
			startLoopItems.append((loopName, loopName, ""))
		if len(startLoopItems) == 0: startLoopItems.append(("NONE", "NONE", ""))
		return startLoopItems
	def selectedLoopChanged(self, context):
		self.updateSockets(self.getStartNode())
		nodeTreeChanged()
	
	selectedLoop = bpy.props.EnumProperty(items = getStartLoopNodeItems, name = "Loop", update=selectedLoopChanged)
	
	def init(self, context):
		forbidCompiling()
		self.updateSockets(self.getStartNode())
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		if self.selectedLoop == "NONE":
			col = layout.column(align = True)
			col.label("New Loop:")
			for loopType in loopTypes:
				row = col.row()
				row.scale_y = 1.3
				newNode = row.operator("node.add_node", text = loopType[0], icon = "PLUS")
				newNode.use_transform = True
				newNode.type = "mn_LoopStartNode"
				setting = newNode.settings.add()
				setting.name = "preset"
				setting.value = repr(loopType[1])
		else:
			layout.prop(self, "selectedLoop")
		layout.separator()
		
	def updateSockets(self, startNode, socketStartValue = (None, None)):
		forbidCompiling()
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
		listSocketType = getListSocketType(socketType)
		if listSocketType == None: return "mn_GenericSocket"
		return listSocketType

	def getStartNode(self):
		return getNodeFromTypeWithAttribute("mn_LoopStartNode", "loopName", self.selectedLoop)

