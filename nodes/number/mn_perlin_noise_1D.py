import bpy, random
from mn_cache import getRandomNoise
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_PerlinNoise1D(Node, AnimationNode):
	bl_idname = "mn_PerlinNoise1D"
	bl_label = "Noise 1D"
	
	additionalSeed = bpy.props.IntProperty(update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "Evolution")
		self.inputs.new("mn_FloatSocket", "Persistance").number = 0.5
		self.inputs.new("mn_IntegerSocket", "Octaves").number = 3.0
		self.outputs.new("mn_FloatSocket", "Noise")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "additionalSeed", text = "Additional Seed")
		
	def getInputSocketNames(self):
		return {"Evolution" : "x",
				"Persistance" : "persistance",
				"Octaves" : "octaves"}
	def getOutputSocketNames(self):
		return {"Noise" : "noise"}
		
	def execute(self, x, persistance, octaves):
		total = 0
		
		for i in range(octaves):
			frequency = 2**i
			amplitude = persistance**i
			total += interpolatedNoise(x * frequency + 823 * self.additionalSeed) * amplitude
			
		return total
		
def interpolatedNoise(x):
	intX = int(x)
	v1 = smoothedNoise(intX)
	v2 = smoothedNoise(intX + 1)
	v3 = smoothedNoise(intX + 2)
	v4 = smoothedNoise(intX + 3)
	return cubicInterpolation(v1, v2, v3, v4, x - intX)
	
def smoothedNoise(x):
	return getRandomNoise(x)/2.0 + getRandomNoise(x-1)/4.0 + getRandomNoise(x+1)/4.0
	
def cubicInterpolation(v0, v1, v2, v3, x):
	p = v3 - v2 + v0 + v1
	return p * x**3 + ((v0 - v1) - p) * x**2 + (v2 - v0) * x + v1
	
	# P = (v3 - v2) - (v0 - v1)
	# Q = (v0 - v1) - P
	# R = v2 - v0
	# S = v1

	# return P*x**3 + Q*x**2 + R*x + S
