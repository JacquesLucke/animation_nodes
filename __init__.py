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

import bpy, sys, os
from bpy.types import NodeTree, Node, NodeSocket
currentPath = os.path.dirname(__file__)
sys.path.append(currentPath)
sys.path.append(currentPath + "\\nodes")

import mn_tree
import mn_node_helper
import mn_sockets
import mn_execution
import mn_input_nodes
import mn_string_operation_nodes
import mn_conversion_nodes
import mn_number_operations
import mn_attribute_output
import mn_object_nodes


bl_info = {
	"name":        "Monodes",
	"description": "Node system for more flexible animations.",
	"author":      "Jacques Lucke",
	"version":     (0, 0, 1),
	"blender":     (2, 7, 2),
	"location":    "Node Editor",
	"category":    "Animation",
	"warning":	   "alpha"
	}
	
	
	
# register
##################################

def register():
	mn_tree.register()
	mn_node_helper.register()
	mn_sockets.register()
	mn_execution.register()
	mn_input_nodes.register()
	mn_string_operation_nodes.register()
	mn_conversion_nodes.register()
	mn_number_operations.register()
	mn_object_nodes.register()
	mn_attribute_output.register()

def unregister():
	mn_tree.unregister()
	mn_node_helper.unregister()
	mn_sockets.unregister()
	mn_execution.unregister()
	mn_input_nodes.unregister()
	mn_string_operation_nodes.unregister()
	mn_conversion_nodes.unregister()
	mn_number_operations.unregister()
	mn_object_nodes.unregister()
	mn_attribute_output.unregister()

if __name__ == "__main__":
	register()