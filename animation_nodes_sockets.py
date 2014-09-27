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

class ObjectSocket(NodeSocket):
	bl_idname = "ObjectSocket"
	bl_label = "Object Socket"
	
	stringProperty = bpy.props.StringProperty()
	
	def draw(self, context, layout, node, text):
		if self.is_output or (not self.is_output and not self.is_linked):
			col = layout.column()
			row = col.row(align = True)
			row.prop(self, "stringProperty", text = "")
			row.operator("mesh.primitive_cube_add", text = "", icon = "EYEDROPPER")
			col.separator()
		else:
			layout.label(text)
		
	def draw_color(self, context, node):
		return (0, 0, 0, 1)
	
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)