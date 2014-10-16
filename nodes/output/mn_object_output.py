import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ObjectOutputNode(Node, AnimationNode):
	bl_idname = "mn_ObjectOutputNode"
	bl_label = "Object Output"
	
	useLocation = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	useRotation = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	useScale = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("VectorSocket", "Location")
		self.inputs.new("VectorSocket", "Rotation")
		self.inputs.new("VectorSocket", "Scale").vector = (1, 1, 1)
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
		
	def execute(self, input):
		object = input["Object"]
		if object is None:
			return {}
		
		if self.useLocation[0]: object.location[0] = input["Location"][0]
		if self.useLocation[1]: object.location[1] = input["Location"][1]
		if self.useLocation[2]: object.location[2] = input["Location"][2]
		
		if self.useRotation[0]: object.rotation_euler[0] = input["Rotation"][0]
		if self.useRotation[1]: object.rotation_euler[1] = input["Rotation"][1]
		if self.useRotation[2]: object.rotation_euler[2] = input["Rotation"][2]
		
		if self.useScale[0]: object.scale[0] = input["Scale"][0]
		if self.useScale[1]: object.scale[1] = input["Scale"][1]
		if self.useScale[2]: object.scale[2] = input["Scale"][2]
		
		return {}