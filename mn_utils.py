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
	
# simple general functions
##########################
	
def getActive():
	return bpy.context.scene.objects.active
def getCurrentFrame():
	return bpy.context.scene.frame_current_final
def getRandom(min, max):
	return random.random() * (max - min) + min
def getRandomString(length):
	return ''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(length))
def clampInt(value, minValue, maxValue):
	return int(max(min(value, maxValue), minValue))
	
# nodes and sockets
######################

def getNode(treeName, nodeName):
	return bpy.data.node_groups[treeName].nodes[nodeName]
def getSocketFromNode(node, isOutputSocket, name):
	if isOutputSocket:
		return node.outputs.get(name)
	else:
		return node.inputs.get(name)
def getNodeIdentifier(node):
	return node.id_data.name + node.name
	
def getConnectionDictionaries(node):
	inputSocketConnections = {}
	outputSocketConnections = {}
	for socket in node.inputs:
		value = socket.getStoreableValue()
		if hasLinks(socket):
			inputSocketConnections[socket.identifier] = (value, socket.links[0].from_socket)
		else:
			inputSocketConnections[socket.identifier] = (value, None)
	for socket in node.outputs:
		for link in socket.links:
			outputSocketConnections[socket.identifier] = link.to_socket
	return (inputSocketConnections, outputSocketConnections)
def tryToSetConnectionDictionaries(node, connections):
	nodeTree = node.id_data
	#inputs
	inputConnections = connections[0]
	for identifier in inputConnections:
		nodeSocket = node.inputs.get(identifier)
		if nodeSocket is not None:
			nodeSocket.setStoreableValue(inputConnections[identifier][0])
			if inputConnections[identifier][1] is not None:
				nodeTree.links.new(nodeSocket, inputConnections[identifier][1])

	#outputs
	outputConnections = connections[1]
	for identifier in outputConnections:
		nodeSocket = node.outputs.get(identifier)
		if nodeSocket is not None:
			nodeTree.links.new(outputConnections[identifier], nodeSocket)
	
# socket origins
######################
	
def isSocketLinked(socket):
	origin = getOriginSocket(socket)
	return origin is not None and origin is not socket
	
def isOtherOriginSocket(socket, origin):
	return origin is not None and origin.node.name != socket.node.name
		
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
	

# fCurves
######################

def getFCurveWithDataPath(object, dataPath, index = 0):
	fCurves = getFCurvesWithDataPath(object, dataPath)
	for fCurve in fCurves:
		if fCurve.array_index == index:
			return fCurve
	return None
def getFCurvesWithDataPath(object, dataPath):
	fcurves = []
	if hasActionData(object):
		for fcurve in object.animation_data.action.fcurves:
			if fcurve.data_path == dataPath:
				fcurves.append(fcurve)
	return fcurves
def hasActionData(object):
	if hasAnimationData(object):
		if object.animation_data.action is not None:
		 return True
	return False
def hasAnimationData(object):
	if object.animation_data is not None:
		return True
	return False