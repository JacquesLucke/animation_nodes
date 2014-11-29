import bpy, random
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.utils.mn_node_utils import *
from animation_nodes.sockets.mn_socket_info import *
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ShuffleListNode(Node, AnimationNode):
	bl_idname = "mn_ShuffleListNode"
	bl_label = "Shuffle List"
	
	def init(self, context):
		forbidCompiling()
		self.generateSockets()
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"List" : "list",
				"Seed" : "seed"}
	def getOutputSocketNames(self):
		return {"Shuffled List" : "shuffledList"}
		
	def execute(self, list, seed):
		random.seed(seed)
		list = list[:] # make a new copy of this list
		random.shuffle(list)
		return list
		
	def update(self):
		nodeTree = self.id_data
		treeInfo = NodeTreeInfo(nodeTree)
		originSocket = treeInfo.getDataOriginSocket(self.inputs.get("List"))
		targetSockets = treeInfo.getDataTargetSockets(self.outputs.get("Shuffled List"))
		
		forbidCompiling()
		if originSocket is not None and len(targetSockets) == 0:
			self.generateSockets(originSocket.bl_idname)
			nodeTree.links.new(self.inputs.get("List"), originSocket)
		if originSocket is None and len(targetSockets) == 1:
			self.generateSockets(targetSockets[0].bl_idname)
			nodeTree.links.new(targetSockets[0], self.outputs.get("Shuffled List"))
		allowCompiling()
		
	def generateSockets(self, listIdName = "mn_ObjectListSocket"):
		if listIdName is None: return
		if listIdName == getattr(self.inputs.get("List"), "bl_idname", None): return
		if not isListSocketType(listIdName): return
		
		forbidCompiling()
		self.inputs.clear()
		self.outputs.clear()
		self.inputs.new(listIdName, "List")
		self.inputs.new("mn_IntegerSocket", "Seed")
		self.outputs.new(listIdName, "Shuffled List")
		allowCompiling()

