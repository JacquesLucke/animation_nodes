import bpy, random
from mn_math_utils import perlinNoise
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_PerlinNoise1D(Node, AnimationNode):
	bl_idname = "mn_PerlinNoise1D"
	bl_label = "Number Wiggle"
	
	additionalSeed = bpy.props.IntProperty(update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "Evolution")
		self.inputs.new("mn_FloatSocket", "Slowness").number = 15.0
		self.inputs.new("mn_FloatSocket", "Amplitude").number = 1
		self.inputs.new("mn_FloatSocket", "Persistance").number = 0.3
		self.inputs.new("mn_IntegerSocket", "Octaves").number = 2.0
		self.outputs.new("mn_FloatSocket", "Noise")
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
		return {"Noise" : "noise"}
		
	def execute(self, x, slowness, amplitude, persistance, octaves):
		x = x / slowness + 823 * self.additionalSeed
		total = perlinNoise(x, persistance, octaves)
		return total * amplitude
		
