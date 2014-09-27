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
	
def getActive():
	return bpy.context.scene.objects.active
	
def getNode(treeName, nodeName):
	return bpy.data.node_groups[treeName].nodes[nodeName]
def getSocketFromNode(node, isOutputSocket, name):
	if isOutputSocket:
		return node.outputs.get(name)
	else:
		return node.inputs.get(name)