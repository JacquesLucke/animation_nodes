import bpy
from mn_utils import *

# Cache some often used data
############################	
		
class CachePerNode:
	def __init__(self):
		self.objects = {}
	def clear(self):
		self.objects = {}
	def getObjectFromNode(self, node):
		treeName = node.id_data.name
		nodeName = node.name
		if treeName in self.objects:
			if nodeName in self.objects[treeName]:
				return self.objects[treeName][nodeName]
		return None
	def setObjectFromNode(self, node, object):
		treeName = node.id_data.name
		nodeName = node.name
		if treeName not in self.objects:
			self.objects[treeName] = {}
		self.objects[treeName][nodeName] = object

class CachePerSocket:
	def __init__(self):
		self.objects = {}
	def clear(self):
		self.objects = {}
		
	def getObjectFromSocket(self, socket):
		identifier = self.getSocketIdentifier(socket)
		if identifier in self.objects:
			return self.objects[identifier]
		else: return None
	def setObjectForSocket(self, socket, object):
		identifier = self.getSocketIdentifier(socket)
		self.objects[identifier] = object
		
	def getSocketIdentifier(self, socket):
		return socket.node.id_data.name + socket.node.name + socket.identifier
	

class AnimationTreeCache:
	def __init__(self):
		self.dependencies = CachePerNode()
		self.originSockets = CachePerSocket()
	def clear(self):
		self.dependencies.clear()
		self.originSockets.clear()
		
	def getDependencyNodeNames(self, node):
		return self.dependencies.getObjectFromNode(node)
	def setNodeDependencies(self, node, dependencies):
		self.dependencies.setObjectFromNode(node, dependencies)
		
	def getOriginSocket(self, socket):
		data = self.originSockets.getObjectFromSocket(socket)
		if data is None:
			return None
		(treeName, nodeName, output, socketName) = data
		node = getNode(treeName, nodeName)
		if output:
			return node.outputs[socketName]
		else:
			return node.inputs[socketName]
	def setOriginSocket(self, socket, origin):
		treeName = origin.node.id_data.name
		nodeName = origin.node.name
		output = origin.is_output
		socketName = origin.name
		self.originSockets.setObjectForSocket(socket, (treeName, nodeName, output, socketName))