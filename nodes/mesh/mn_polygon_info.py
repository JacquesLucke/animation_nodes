import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_PolygonInfo(Node, AnimationNode):
	bl_idname = "mn_PolygonInfo"
	bl_label = "Polygon Info"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_PolygonSocket", "Polygon")
		self.outputs.new("mn_VectorSocket", "Center")
		self.outputs.new("mn_VectorSocket", "Normal")
		self.outputs.new("mn_FloatSocket", "Area")
		self.outputs.new("mn_IntegerSocket", "Material Index")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Polygon" : "polygon"}
	def getOutputSocketNames(self):
		return {"Center" : "center",
				"Normal" : "normal",
				"Area" : "area",
				"Material Index" : "materialIndex"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		if outputUse["Center"]: codeLines.append("$center$ = %polygon%[0]")
		if outputUse["Normal"]: codeLines.append("$normal$ = %polygon%[1]")
		if outputUse["Area"]: codeLines.append("$area$ = %polygon%[2]")
		if outputUse["Material Index"]: codeLines.append("$materialIndex$ = %polygon%[3]")
		return "\n".join(codeLines)
		