import bpy
from bpy.types import Node
from mathutils import *
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ComposeMatrix(Node, AnimationNode):
	bl_idname = "mn_ComposeMatrix"
	bl_label = "Compose Matrix"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VectorSocket", "Position")
		self.inputs.new("mn_VectorSocket", "Rotation")
		self.inputs.new("mn_VectorSocket", "Scale").vector = [1, 1, 1]
		self.outputs.new("mn_MatrixSocket", "Matrix")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Position" : "position",
				"Rotation" : "rotation",
				"Scale" : "scale"}
	def getOutputSocketNames(self):
		return {"Matrix" : "matrix"}

	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		codeLines.append("$matrix$ = mathutils.Matrix.Translation(%position%)")
		codeLines.append("$matrix$ *= mathutils.Matrix.Rotation(%rotation%[2], 4, 'Z')")
		codeLines.append("$matrix$ *= mathutils.Matrix.Rotation(%rotation%[1], 4, 'Y')")
		codeLines.append("$matrix$ *= mathutils.Matrix.Rotation(%rotation%[0], 4, 'X')")
		codeLines.append("$matrix$ *= mathutils.Matrix.Scale(%scale%[0], 4, [1, 0, 0])")
		codeLines.append("$matrix$ *= mathutils.Matrix.Scale(%scale%[1], 4, [0, 1, 0])")
		codeLines.append("$matrix$ *= mathutils.Matrix.Scale(%scale%[2], 4, [0, 0, 1])")
		return "\n".join(codeLines)
		
	def getModuleList(self):
		return ["mathutils"]