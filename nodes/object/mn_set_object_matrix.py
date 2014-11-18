import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

outputItems = [	("BASIS", "Basis", ""),
				("LOCAL", "Local", ""),
				("PARENT INVERSE", "Parent Inverse", ""),
				("WORLD", "World", "") ]

class mn_ObjectMatrixOutputNode(Node, AnimationNode):
	bl_idname = "mn_ObjectMatrixOutputNode"
	bl_label = "Object Matrix Output"
	
	outputType = bpy.props.EnumProperty(items = outputItems, update = nodeTreeChanged, default = "WORLD")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_MatrixSocket", "Matrix")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "outputType", text = "Type")
		
	def getInputSocketNames(self):
		return {"Object" : "object",
				"Matrix" : "matrix"}
	def getOutputSocketNames(self):
		return {}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		t = self.outputType
		codeLines = []
		codeLines.append("if %object% is not None:")
		if t == "BASIS": codeLines.append("    %object%.matrix_basis = %matrix%")
		if t == "LOCAL": codeLines.append("    %object%.matrix_local = %matrix%")
		if t == "PARENT INVERSE": codeLines.append("    %object%.matrix_parent_inverse = %matrix%")
		if t == "WORLD": codeLines.append("    %object%.matrix_world = %matrix%")
		return "\n".join(codeLines)


classes = [
	mn_ObjectMatrixOutputNode
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
