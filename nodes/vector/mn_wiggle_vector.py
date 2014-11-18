import bpy, random
from animation_nodes.utils.mn_math_utils import perlinNoise
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_VectorWiggle(Node, AnimationNode):
	bl_idname = "mn_VectorWiggle"
	bl_label = "Vector Wiggle"
	isDetermined = True
	
	additionalSeed = bpy.props.IntProperty(update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "Seed")
		self.inputs.new("mn_FloatSocket", "Time")
		self.inputs.new("mn_FloatSocket", "Speed").number = 15.0
		self.inputs.new("mn_VectorSocket", "Amplitude").vector = [5, 5, 5]
		self.inputs.new("mn_FloatSocket", "Persistance").number = 0.3
		self.inputs.new("mn_IntegerSocket", "Octaves").number = 2.0
		self.outputs.new("mn_VectorSocket", "Vector")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "additionalSeed", text = "Additional Seed")
		
	def getInputSocketNames(self):
		return {"Seed" : "seed",
				"Time" : "time",
				"Speed" : "speed",
				"Amplitude" : "amplitude",
				"Persistance" : "persistance",
				"Octaves" : "octaves"}
	def getOutputSocketNames(self):
		return {"Vector" : "vector"}
		
	def execute(self, seed, time, speed, amplitude, persistance, octaves):
		vector = [0, 0, 0]
		time = time / speed + 2541 * seed + 823 * self.additionalSeed
		vector[0] = perlinNoise(time, persistance, octaves) * amplitude[0]
		time += 79
		vector[1] = perlinNoise(time, persistance, octaves) * amplitude[1]
		time += 263
		vector[2] = perlinNoise(time, persistance, octaves) * amplitude[2]
		return vector
		


classes = [
	mn_VectorWiggle
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
