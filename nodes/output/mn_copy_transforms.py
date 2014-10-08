import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged
from mn_object_utils import *
from mn_utils import *

class CopyTransformsNode(Node, AnimationNode):
	bl_idname = "CopyTransformsNode"
	bl_label = "Copy Transforms"
	
	useLocation = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	useRotation = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	useScale = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	
	frameTypes = [
		("OFFSET", "Offset", ""),
		("ABSOLUTE", "Absolute", "") ]
	frameTypesProperty = bpy.props.EnumProperty(name = "Frame Type", items = frameTypes, default = "OFFSET")
	
	def init(self, context):
		fromSocket = self.inputs.new("ObjectSocket", "From")
		fromSocket.showName = True
		toSocket = self.inputs.new("ObjectSocket", "To")
		toSocket.showName = True
		self.inputs.new("FloatSocket", "Frame")
		self.outputs.new("ObjectSocket", "To")
		self.width = 200
		
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
		row.label("Scale")
		row.prop(self, "useScale", index = 0, text = "X")
		row.prop(self, "useScale", index = 1, text = "Y")
		row.prop(self, "useScale", index = 2, text = "Z")
		
		layout.prop(self, "frameTypesProperty")
		
	def execute(self, input):
		fromObject = input["From"]
		toObject = input["To"]
		if fromObject is None or toObject is None:
			return { "To" : None }
			
		if self.frameTypesProperty == "OFFSET":
			frame = getCurrentFrame()
			frame += input["Frame"]
		elif self.frameTypesProperty == "ABSOLUTE":
			frame = input["Frame"]
			
		location, rotation, scale = getObjectTransformsAtFrame(fromObject, frame)
		
		if self.useLocation[0]: toObject.location[0] = location[0]
		if self.useLocation[1]: toObject.location[1] = location[1]
		if self.useLocation[2]: toObject.location[2] = location[2]
		
		if self.useRotation[0]: toObject.rotation_euler[0] = rotation[0]
		if self.useRotation[1]: toObject.rotation_euler[1] = rotation[1]
		if self.useRotation[2]: toObject.rotation_euler[2] = rotation[2]
		
		if self.useScale[0]: toObject.scale[0] = scale[0]
		if self.useScale[1]: toObject.scale[1] = scale[1]
		if self.useScale[2]: toObject.scale[2] = scale[2]
		
		return { "To" : toObject}
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)