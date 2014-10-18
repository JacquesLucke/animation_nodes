import bpy, random
from mn_math_utils import perlinNoise
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_VectorWiggle(Node, AnimationNode):
	bl_idname = "mn_VectorWiggle"
	bl_label = "Vector Wiggle"
	
	additionalSeed = bpy.props.IntProperty(update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "Evolution")
		self.inputs.new("mn_FloatSocket", "Slowness").number = 15.0
		self.inputs.new("mn_VectorSocket", "Amplitude").vector = [5, 5, 5]
		self.inputs.new("mn_FloatSocket", "Persistance").number = 0.3
		self.inputs.new("mn_IntegerSocket", "Octaves").number = 2.0
		self.outputs.new("mn_VectorSocket", "Vector")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "additionalSeed", text = "Additional Seed")
		
	def getInputSocketNames(self):
		return {"Evolution" : "x",
				"Slowness" : "slowness",
				"Amplitude" : "amplitude",
				"Persistance" : "persistance",
				"Octaves" : "octaves"}
	def getOutputSocketNames(self):
		return {"Vector" : "vector"}
		
	def execute(self, x, slowness, amplitude, persistance, octaves):
		vector = [0, 0, 0]
		x = x / slowness + 823 * self.additionalSeed
		vector[0] = perlinNoise(x, persistance, octaves) * amplitude[0]
		x += 79
		vector[1] = perlinNoise(x, persistance, octaves) * amplitude[1]
		x += 263
		vector[2] = perlinNoise(x, persistance, octaves) * amplitude[2]
		return vector
		
