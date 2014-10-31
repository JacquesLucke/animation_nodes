import bpy
from bpy.types import Node
from mathutils import *
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_TranslationMatrix(Node, AnimationNode):
	bl_idname = "mn_TranslationMatrix"
	bl_label = "Translation Matrix"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VectorSocket", "Translation")
		self.outputs.new("mn_MatrixSocket", "Matrix")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Translation" : "translation"}
	def getOutputSocketNames(self):
		return {"Matrix" : "matrix"}

	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		return "$matrix$ = mathutils.Matrix.Translation(%translation%)"
		
	def getModuleList(self):
		return ["mathutils"]
		
	def copy(self, node):
		self.inputs[0].vector = [0, 0, 0]