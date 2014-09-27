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


import bpy
from bpy.types import NodeTree, Node, NodeSocket
from animation_nodes_nodes import AnimationNode	
	
		
class ObjectInputNode(Node, AnimationNode):
	bl_idname = "ObjectInputNode"
	bl_label = "Object Input"
	
	objectName = bpy.props.StringProperty()
	
	def init(self, context):
		self.outputs.new("ObjectSocket", "Object")
		
	def draw_buttons(self, context, layout):
		col = layout.column()
		row = col.row(align = True)
		row.prop(self, "objectName", text = "")
		selector = row.operator("animation_nodes.assign_active_object_to_node", text = "", icon = "EYEDROPPER")
		selector.nodeTreeName = self.id_data.name
		selector.nodeName = self.name
		selector.target = "objectName"
		col.separator()
		
	def execute(self, input):
		output = {}
		output["Object"] = self.objectName
		return output
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)