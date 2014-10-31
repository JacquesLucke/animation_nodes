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
		self.outputs.new("mn_MatrixSocket", "Basis")
		self.outputs.new("mn_MatrixSocket", "Local")
		self.outputs.new("mn_MatrixSocket", "Parent Inverse")
		self.outputs.new("mn_MatrixSocket", "World")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Object" : "object"}
	def getOutputSocketNames(self):
		return {"Basis" : "basis",
				"Local" : "local",
				"Parent Inverse" : "parentInverse",
				"World" : "world"}
		
	def execute(self, useOutput, object):
		if object is None:
			return Matrix.Identity(4), Matrix.Identity(4), Matrix.Identity(4), Matrix.Identity(4)
			
		return object.matrix_basis, object.matrix_local, object.matrix_parent_inverse, object.matrix_world