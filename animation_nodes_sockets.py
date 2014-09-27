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
from animation_nodes_utils import *

class ObjectSocket(NodeSocket):
	bl_idname = "ObjectSocket"
	bl_label = "Object Socket"
	
	stringProperty = bpy.props.StringProperty()
	
	def draw(self, context, layout, node, text):
		if self.is_output or (not self.is_output and not self.is_linked):
			col = layout.column()
			row = col.row(align = True)
			row.prop(self, "stringProperty", text = "")
			selector = row.operator("animation_nodes.assign_active_object_to_node", text = "", icon = "EYEDROPPER")
			selector.nodeTreeName = node.id_data.name
			selector.nodeName = node.name
			col.separator()
		else:
			layout.label(text)
		
	def draw_color(self, context, node):
		return (0, 0, 0, 1)
		
		
class AssignActiveObjectToNode(bpy.types.Operator):
	bl_idname = "animation_nodes.assign_active_object_to_node"
	bl_label = "Assign Active Object"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		obj = getActive()
		bpy.data.node_groups[self.nodeTreeName].nodes[self.nodeName].outputs[0].stringProperty = obj.name
		print(obj.name)
		print(bpy.data.node_groups[self.nodeTreeName].nodes[self.nodeName].outputs[0].stringProperty)
		return {'FINISHED'}
	
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)