'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import bpy, random
from bpy.types import NodeTree, Node, NodeSocket
from mn_node_helper import AnimationNode
from mn_utils import *
from mn_execution import nodePropertyChanged


class StringInputNode(Node, AnimationNode):
	bl_idname = "StringInputNode"
	bl_label = "String"
	
	stringProperty = bpy.props.StringProperty(default = "text", update = nodePropertyChanged)
	
	def init(self, context):
		self.outputs.new("StringSocket", "Text")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "stringProperty", text = "")
		
	def execute(self, input):
		output = {}
		output["Text"] = self.stringProperty
		return output
		
		
class ObjectInputNode(Node, AnimationNode):
	bl_idname = "ObjectInputNode"
	bl_label = "Object"
	
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	
	def init(self, context):
		self.outputs.new("ObjectSocket", "Object")
		
	def draw_buttons(self, context, layout):
		col = layout.column()
		row = col.row(align = True)
		row.prop(self, "objectName", text = "")
		selector = row.operator("mn.assign_active_object_to_node", text = "", icon = "EYEDROPPER")
		selector.nodeTreeName = self.id_data.name
		selector.nodeName = self.name
		selector.target = "objectName"
		col.separator()
		
	def execute(self, input):
		output = {}
		output["Object"] = self.objectName
		return output
		
class TimeInfoNode(Node, AnimationNode):
	bl_idname = "TimeInfoNode"
	bl_label = "Time Info"
	
	def init(self, context):
		self.outputs.new("IntegerSocket", "Frame")
		
	def execute(self, input):
		output = {}
		output["Frame"] = getCurrentFrame()
		return output
		
class RandomFloatNode(Node, AnimationNode):
	bl_idname = "RandomFloatNode"
	bl_label = "Random Float"
	
	def init(self, context):
		self.inputs.new("IntegerSocket", "Seed")
		self.inputs.new("FloatSocket", "Min").number = 0.0
		self.inputs.new("FloatSocket", "Max").number = 1.0
		self.outputs.new("FloatSocket", "Value")
		
	def execute(self, input):
		output = {}
		seed = input["Seed"]
		min = input["Min"]
		max = input["Max"]
		random.seed(seed)
		output["Value"] = random.uniform(min, max)
		return output
		
class RandomStringNode(Node, AnimationNode):
	bl_idname = "RandomStringNode"
	bl_label = "Random Text"
	
	def init(self, context):
		self.inputs.new("IntegerSocket", "Seed")
		self.inputs.new("IntegerSocket", "Length").number = 5
		self.inputs.new("StringSocket", "Characters").string = "abcdefghijklmnopqrstuvwxyz"
		self.outputs.new("StringSocket", "Text")
		
	def execute(self, input):
		output = {}
		seed = input["Seed"]
		length = input["Length"]
		characters = input["Characters"]
		random.seed(seed)
		output["Text"] = ''.join(random.choice(characters) for _ in range(length))
		return output
		
class CharactersNode(Node, AnimationNode):
	bl_idname = "CharactersNode"
	bl_label = "Characters"
	
	def init(self, context):
		self.outputs.new("StringSocket", "Lower Case")
		self.outputs.new("StringSocket", "Upper Case")
		self.outputs.new("StringSocket", "Digits")
		self.outputs.new("StringSocket", "Special")
		self.outputs.new("StringSocket", "All")
		
	def execute(self, input):
		output = {}
		output["Lower Case"] = "abcdefghijklmnopqrstuvwxyz"
		output["Upper Case"] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		output["Digits"] = "0123456789"
		output["Special"] = "!§$%&/()=?*+#'-_.:,;" + '"'
		output["All"] = output["Lower Case"] + output["Upper Case"] + output["Digits"] + output["Special"]
		return output
	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)