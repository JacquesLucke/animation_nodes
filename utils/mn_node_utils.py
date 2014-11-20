import bpy
from animation_nodes.mn_utils import *

def getPossibleNodeName(nodeTree, name = "node"):
	randomString = getRandomString(3)
	counter = 1
	while nodeTree.nodes.get(name + randomString + str(counter)) is not None:
		counter += 1
	return name + randomString + str(counter)
	

def getAttributesFromNodesWithType(nodeType, attribute):
	data = []
	nodes = getNodesFromType(nodeType)
	for node in nodes:
		data.append(getattr(node, attribute))
	return data

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
		if nodeTree.bl_idname == "mn_AnimationNodeTree":
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
	
	
def removeLinksFromSocket(socket):
	if socket is None: return
	allLinks = socket.node.id_data.links
	for link in socket.links:
		allLinks.remove(link)
	

def updateDependencyNode(socket):
	if socket is not None:
		if len(socket.links) == 1:
			fromNode = socket.links[0].from_node
			if hasattr(fromNode, "update"):
				fromNode.update()
				
class NodeTreeInfo:
	def __init__(self, nodeTree):
		self.nodeTree = nodeTree
		self.nodes = nodeTree.nodes
		self.links = nodeTree.links
		
		self.inputSockets = {}
		self.outputSockets = {}
		self.updateSettings = {}
		
		self.createConnectionDics()
		
	def createConnectionDics(self):
		for link in self.links:
			fromSocket = link.from_socket
			toSocket = link.to_socket
			if isReroute(toSocket): continue
			originSocket = fromSocket
			if isReroute(fromSocket): originSocket = getOriginSocket(toSocket)
			if isOtherOriginSocket(toSocket, originSocket):
				self.setConnection(originSocket, toSocket)
	def setConnection(self, fromSocket, toSocket):
		if toSocket.bl_idname == "mn_NodeNetworkSocket":
			self.updateSettings[fromSocket.node] = toSocket.node
		else:
			if fromSocket not in self.outputSockets:
				self.outputSockets[fromSocket] = []
			if toSocket not in self.inputSockets:
				self.inputSockets[toSocket] = []
			self.outputSockets[fromSocket].append(toSocket)
			self.inputSockets[toSocket].append(fromSocket)
			
	def getDataOriginSockets(self, socket):
		return self.inputSockets.get(socket, [])
	def getDataTargetSockets(self, socket):
		return self.outputSockets.get(socket, [])
	def getDataOriginSocket(self, socket):
		originSockets = self.inputSockets.get(socket)
		if originSockets is not None:
			return originSockets[0]
		return None
	def getDataOriginNode(self, socket):
		originSocket = self.getDataOriginSocket(socket)
		if originSocket is not None:
			return originSocket.node
		return None
	def getDirectLinkedNodes(self, node):
		linkedNodes = set()
		linkedNodes.update(self.getDirectParentNodes(node))
		linkedNodes.update(self.getDirectChildrenNodes(node))
		return linkedNodes
	def getDirectParentNodes(self, node):
		parentNodes = set()
		for socket in node.inputs:
			originSockets = self.getDataOriginSockets(socket)
			for originSocket in originSockets:
				parentNodes.update([originSocket.node])
		return parentNodes
	def getDirectChildrenNodes(self, node):
		childrenNodes = set()
		for socket in node.outputs:
			targetSockets = self.getDataTargetSockets(socket)
			for targetSocket in targetSockets:
				childrenNodes.update([targetSocket.node])
		return childrenNodes
	def getNodesInNetwork(self, node):
		networkNodes = []
		uncheckedNodes = [node]
		while len(uncheckedNodes) > 0:
			checkNode = uncheckedNodes[-1]
			linkedNodes = self.getDirectLinkedNodes(checkNode)
			del uncheckedNodes[-1]
			for node in linkedNodes:
				if node not in uncheckedNodes and node not in networkNodes:
					uncheckedNodes.append(node)
			networkNodes.append(checkNode)
		return networkNodes
		
def isReroute(object):
	if isinstance(object, bpy.types.Node):
		return object.bl_idname == "NodeReroute"
	if isinstance(object, bpy.types.NodeSocket):
		return object.node.bl_idname == "NodeReroute"
	return False