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
			total += interpolatedNoise(x * frequency) * amplitude
			
		return total
		
def interpolatedNoise(x):
	intX = int(x)
	fraction = x - intX
	v1 = smoothedNoise(intX)
	v2 = smoothedNoise(intX + 1)
	v3 = smoothedNoise(intX + 2)
	v4 = smoothedNoise(intX + 3)
	return cubicInterpolation(v1, v2, v3, v4, fraction)
	
def smoothedNoise(x):
	return getRandomNoise(x)/2.0 + getRandomNoise(x-1)/4.0 + getRandomNoise(x+1)/4.0
	
def cubicInterpolation(v0, v1, v2, v3, x):
	p = (v3 - v2) - (v0 - v1)
	q = (v0 - v1) - p
	r = v2 - v0
	s = v1
	return p * x**3 + q * x**2 + r * x + s
	
def interpolate(a, b, x):
	ft = x * 3.1415927
	f = (1.0 - cos(ft)) * 0.5
	return a*(1.0-f) + b*f