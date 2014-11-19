import bpy, random
from bpy.types import Node
from animation_nodes.mn_cache import getUniformRandom
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_RandomVectorNode(Node, AnimationNode):
	bl_idname = "mn_RandomVectorNode"
	bl_label = "Random Vector"
	isDetermined = True
	
	additionalSeed = bpy.props.IntProperty(update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Seed")
		self.inputs.new("mn_FloatSocket", "Max Values").number = 5.0
		self.outputs.new("mn_VectorSocket", "Vector")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "additionalSeed", text = "Additional Seed")
		
	def getInputSocketNames(self):
		return {"Seed" : "seed", "Max Values" : "maxValues"}
	def getOutputSocketNames(self):
		return {"Vector" : "random_vector"}
		
	def execute(self, seed, maxValues):
		max = maxValues/2
		return [getUniformRandom(seed + 1193 * self.additionalSeed, -max, max),
				getUniformRandom(seed + 754 + 1193 * self.additionalSeed, -max, max),
				getUniformRandom(seed + 2345 + 1193 * self.additionalSeed, -max, max)]
				
	def copy(self, node):
		self.additionalSeed = int(random.random()*1000)
		

