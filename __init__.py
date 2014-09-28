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

import animation_nodes_tree
import animation_nodes_node_helper
import animation_nodes_sockets
import animation_nodes_execution
import animation_nodes_input_nodes
import animation_nodes_string_operation_nodes
import animation_nodes_conversion_nodes
import animation_nodes_number_operations


bl_info = {
	"name":        "Animation Nodes",
	"description": "",
	"author":      "Jacques Lucke",
	"version":     (0, 0, 1),
	"blender":     (2, 7, 2),
	"location":    "Node Editor",
	"category":    "Animation",
	"warning":	   "pre alpha"
	}
	
	
	
# register
##################################

def register():
	animation_nodes_tree.register()
	animation_nodes_node_helper.register()
	animation_nodes_sockets.register()
	animation_nodes_execution.register()
	animation_nodes_input_nodes.register()
	animation_nodes_string_operation_nodes.register()
	animation_nodes_conversion_nodes.register()
	animation_nodes_number_operations.register()

def unregister():
	animation_nodes_tree.unregister()
	animation_nodes_node_helper.unregister()
	animation_nodes_sockets.unregister()
	animation_nodes_execution.unregister()
	animation_nodes_input_nodes.unregister()
	animation_nodes_string_operation_nodes.unregister()
	animation_nodes_conversion_nodes.unregister()
	animation_nodes_number_operations.unregister()

if __name__ == "__main__":
	register()