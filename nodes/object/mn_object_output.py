import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_ObjectOutputNode(Node, AnimationNode):
	bl_idname = "mn_ObjectOutputNode"
	bl_label = "Transforms Output"
	
	useLocation = bpy.props.BoolVectorProperty(update = nodeTreeChanged)
	useRotation = bpy.props.BoolVectorProperty(update = nodeTreeChanged)
	useScale = bpy.props.BoolVectorProperty(update = nodeTreeChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_VectorSocket", "Location")
		self.inputs.new("mn_VectorSocket", "Rotation")
		self.inputs.new("mn_VectorSocket", "Scale").vector = (1, 1, 1)
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		col = layout.column(align = True)
		
		row = col.row(align = True)
		row.label("Location")
		row.prop(self, "useLocation", index = 0, text = "X")
		row.prop(self, "useLocation", index = 1, text = "Y")
		row.prop(self, "useLocation", index = 2, text = "Z")
		row = col.row(align = True)
		row.label("Rotation")
		row.prop(self, "useRotation", index = 0, text = "X")
		row.prop(self, "useRotation", index = 1, text = "Y")
		row.prop(self, "useRotation", index = 2, text = "Z")
		row = col.row(align = True)
		row.label("cale")
		row.prop(self, "useScale", index = 0, text = "X")
		row.prop(self, "useScale", index = 1, text = "Y")
		row.prop(self, "useScale", index = 2, text = "Z")
		
	def getInputSocketNames(self):
		return {"Object" : "object",
				"Location" : "location",
				"Rotation" : "rotation",
				"Scale" : "scale"}
	def getOutputSocketNames(self):
		return {}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		useLoc = self.useLocation
		useRot = self.useRotation
		useScale = self.useScale
		
		codeLines = []
		codeLines.append("if %object% is not None:")
		
		# location
		if useLoc[0] and useLoc[1] and useLoc[2]:
			codeLines.append("    %object%.location = %location%")
		else:
			for i in range(3):
				if useLoc[i]: codeLines.append("    %object%.location["+str(i)+"] = %location%["+str(i)+"]")
				
		# rotation		
		if useRot[0] and useRot[1] and useRot[2]:
			codeLines.append("    %object%.rotation_euler = %rotation%")
		else:
			for i in range(3):
				if useRot[i]: codeLines.append("    %object%.rotation_euler["+str(i)+"] = %rotation%["+str(i)+"]")
		
		# scale
		if useScale[0] and useScale[1] and useScale[2]:
			codeLines.append("    %object%.scale = %scale%")
		else:
			for i in range(3):
				if useScale[i]: codeLines.append("    %object%.scale["+str(i)+"] = %scale%["+str(i)+"]")
		
		if not (useLoc[0] or useLoc[1] or useLoc[2] or
				useRot[0] or useRot[1] or useRot[2] or
				useScale[0] or useScale[1] or useScale[2]):
			codeLines = []
		return "\n".join(codeLines)


classes = [
	mn_ObjectOutputNode
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
