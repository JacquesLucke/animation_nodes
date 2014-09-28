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
from animation_nodes_utils import *
	
def getActive():
	return bpy.context.scene.objects.active
def getCurrentFrame():
	return bpy.context.scene.frame_current
	
def getNode(treeName, nodeName):
	return bpy.data.node_groups[treeName].nodes[nodeName]
def getSocketFromNode(node, isOutputSocket, name):
	if isOutputSocket:
		return node.outputs.get(name)
	else:
		return node.inputs.get(name)
		
def getAnimationNodeTrees():
	nodeTrees = []
	for nodeTree in bpy.data.node_groups:
		if hasattr(nodeTree, "isAnimationNodeTree"):
			nodeTrees.append(nodeTree)
	return nodeTrees
	
def isSocketLinked(socket):
	origin = getOriginSocket(socket)
	return origin is not None and origin is not socket
	
def isOtherOriginSocket(socket, origin):
	return origin is not None and origin is not socket
		
def getOriginSocket(socket):
	if hasLinks(socket):
		fromSocket = socket.links[0].from_socket
		if fromSocket.node.type == "REROUTE":
			return getOriginSocket(fromSocket.node.inputs[0])
		else:
			return fromSocket
	else:
		if socket.node.type == "REROUTE":
			return None
		else:
			return socket
		
def hasLinks(socket):
	return len(socket.links) > 0