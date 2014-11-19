import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_FloatRangeListNode(Node, AnimationNode):
	bl_idname = "mn_FloatRangeListNode"
	bl_label = "Number Range"
	node_category = "Math"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Amount").number = 5
		self.inputs.new("mn_FloatSocket", "Start")
		self.inputs.new("mn_FloatSocket", "Step").number = 1
		self.outputs.new("mn_FloatListSocket", "List")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Amount" : "amount", "Start" : "start", "Step" : "step"}
	def getOutputSocketNames(self):
		return {"List" : "list"}
		
	def execute(self, amount, start, step):
		list = []
		for i in range(amount):
			list.append(start + i * step)
		return list

