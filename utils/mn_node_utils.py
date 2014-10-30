import bpy
from mn_utils import *

def getNodeFromTypeWithAttribute(nodeType, attribute, data):
	nodes = getNodesFromTypeWithAttribute(nodeType, attribute, data)
	if len(nodes) > 0: return nodes[0]
	return None

def getNodesFromTypeWithAttribute(nodeType, attribute, data):
	nodes = []
	nodesFromType = getNodesFromType(nodeType)
	for node in nodesFromType:
		if getattr(node, attribute) == data:
			nodes.append(node)
	return nodes

def getNodesFromType(nodeType):
	nodes = []
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:
		for node in nodeTree.nodes:
			if node.bl_idname == nodeType:
				nodes.append(node)
	return nodes
	
def getAnimationNodeTrees():
	nodeTrees = []
	for nodeTree in bpy.data.node_groups:
		if hasattr(nodeTree, "isAnimationNodeTree"):
			nodeTrees.append(nodeTree)
	return nodeTrees
	
	
def getNotUsedSocketName(node, prefix = "socket name"):
	socketName = prefix
	while isSocketNameUsed(node, socketName):
		socketName = prefix + getRandomString(3)
	return socketName
def isSocketNameUsed(node, name):
	for socket in node.outputs:
		if socket.name == name or socket.identifier == name: return True
	for socket in node.inputs:
		if socket.name == name or socket.identifier == name: return True
	return False
	
	
def getNotUsedCustomSocketName(node, prefix = "custom name"):
	customName = prefix
	while isCustomSocketNameUsed(node, customName):
		customName = prefix + getRandomString(3)
	return customName
def isCustomSocketNameUsed(node, customName):
	for socket in node.outputs:
		if socket.customName == customName: return True
	return False
	

def updateDependencyNode(socket):
	if socket is not None:
		if len(socket.links) == 1:
			fromNode = socket.links[0].from_node
			if hasattr(fromNode, "update"):
				fromNode.update()