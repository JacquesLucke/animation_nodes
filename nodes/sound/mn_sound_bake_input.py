import bpy, math
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.utils.mn_object_utils import *
from animation_nodes.nodes.mn_node_helper import *
from animation_nodes.mn_cache import *


class mn_SoundBakeInput(Node, AnimationNode):
	bl_idname = "mn_SoundBakeInput"
	bl_label = "Sound Bake Input"
	
	def getSoundBakeNodeNames(self):
		bakeNodeNames = []
		for node in self.id_data.nodes:
			if node.bl_idname == "mn_SoundBakeNode":
				bakeNodeNames.append(node.name)
		return bakeNodeNames
		
	def getSoundBakeNodeItems(self, context):
		bakeNodeNames = self.getSoundBakeNodeNames()
		bakeNodeItems = []
		for name in bakeNodeNames:
			bakeNodeItems.append((name, name, ""))
		if len(bakeNodeItems) == 0: bakeNodeItems.append(("NONE", "NONE", ""))
		return bakeNodeItems
	
	bakeNodeName = bpy.props.EnumProperty(items = getSoundBakeNodeItems, name = "Bake Node", update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_BakedSoundSocket", "Sound")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		if self.bakeNodeName == "NONE":
			newNode = layout.operator("node.add_node", text = "Sound Bake", icon = "PLUS")
			newNode.type = "mn_SoundBakeNode"
			newNode.use_transform = True
		else:
			layout.prop(self, "bakeNodeName", text = "Sound")
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Sound" : "sound"}
		
	def execute(self):
		return self.id_data.nodes.get(self.bakeNodeName)

classes = [
	mn_SoundBakeInput
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
