import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.utils.mn_node_utils import *
from animation_nodes.sockets.mn_socket_info import *
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_GetListElementNode(Node, AnimationNode):
	bl_idname = "mn_GetListElementNode"
	bl_label = "Get Element"
	
	def init(self, context):
		forbidCompiling()
		self.generateSockets()
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"List" : "list",
				"Index" : "index"}
	def getOutputSocketNames(self):
		return {"Element" : "element"}
		
	def execute(self, list, index):
		length = len(list)
		if length == 0: return self.outputs.get("Element").getValue()
		index = min(max(index, 0), length - 1)
		return list[index]
		
	def update(self):
		nodeTree = self.id_data
		treeInfo = NodeTreeInfo(nodeTree)
		originSocket = treeInfo.getDataOriginSocket(self.inputs.get("List"))
		targetSockets = treeInfo.getDataTargetSockets(self.outputs.get("Element"))
		
		forbidCompiling()
		if originSocket is not None and len(targetSockets) == 0:
			self.generateSockets(originSocket.bl_idname)
			nodeTree.links.new(self.inputs.get("List"), originSocket)
		if originSocket is None and len(targetSockets) == 1:
			self.generateSockets(getListSocketType(targetSockets[0].bl_idname))
			nodeTree.links.new(targetSockets[0], self.outputs.get("Element"))
		allowCompiling()
		
	def generateSockets(self, listIdName = "mn_ObjectListSocket"):
		if listIdName is None: return
		baseIdName = getBaseSocketType(listIdName)
		if baseIdName is None: return
		if listIdName == self.inputs.get("List").bl_idname: return
		
		forbidCompiling()
		self.inputs.clear()
		self.outputs.clear()
		self.inputs.new(listIdName, "List")
		self.inputs.new("mn_IntegerSocket", "Index")
		self.outputs.new(baseIdName, "Element")
		allowCompiling()

