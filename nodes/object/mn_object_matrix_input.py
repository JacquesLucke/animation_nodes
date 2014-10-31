import bpy
from bpy.types import Node
from mathutils import *
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ObjectMatrixInput(Node, AnimationNode):
	bl_idname = "mn_ObjectMatrixInput"
	bl_label = "Object Matrix Input"
	outputUseParameterName = "useOutput"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.outputs.new("mn_MatrixSocket", "World Matrix")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Object" : "object"}
	def getOutputSocketNames(self):
		return {"World Matrix" : "world"}
		
	def execute(self, useOutput, object):
		if object is None:
			return Matrix.Identity(4)
			
		return object.matrix_world