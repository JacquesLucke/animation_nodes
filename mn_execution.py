import bpy, time
from bpy.app.handlers import persistent
from mn_utils import *
from mn_cache import AnimationTreeCache


# execute an individual node tree
##################################

class AnimationNodeTree:
	def __init__(self, nodeTree):
		self.nodeTree = nodeTree
		self.nodes = {}
		for node in nodeTree.nodes:
			if node.type != "REROUTE":
				self.nodes[node.name] = AnimationNode(node)
			
	def execute(self, rebuildDependencyCache = False):
		if rebuildDependencyCache:
			animationTreeCache.clear()
			self.cleanup()
		
		for node in self.nodes.values():
			node.isUpdated = False
		
		for node in self.nodes.values():
			if not node.isUpdated:
				self.updateNode(node)
	
	def cleanup(self):
		self.removeLinksBetweenNotAllowedSocketTypes()
	def removeLinksBetweenNotAllowedSocketTypes(self):
		links = self.nodeTree.links
		for link in links:
			if link.to_node.type == "REROUTE":
				continue
			if not isSocketLinked(link.to_socket):
				continue
			toSocket = link.to_socket
			fromSocket = getOriginSocket(toSocket)
			if fromSocket.dataType not in toSocket.allowedInputTypes:
				self.nodeTree.links.remove(link)
	
	
	# warning: this is a recursion -> these two functions call each other
	def updateNode(self, node):
		self.updateNodeDependenciesIfNecessary(node)
		self.generateInputList(node)
		node.execute()
		node.isUpdated = True
	def updateNodeDependenciesIfNecessary(self, node):
		dependencyNodeNames = node.getDependencyNodeNames()
		for name in dependencyNodeNames:
			if not self.nodes[name].isUpdated:
				self.updateNode(self.nodes[name])
		
	def generateInputList(self, node):
		node.input = {}
		socketPairs = self.getSocketPairs(node)
		for (socket, origin) in socketPairs:
			if isOtherOriginSocket(socket, origin):
				value = self.nodes[origin.node.name].output[origin.identifier] # use value of origin socket
			else:
				value = socket.getValue() # use value of this socket
			node.input[socket.identifier] = value
			
	def getSocketPairs(self, node):
		inputSockets = node.node.inputs
		socketPairs = []
		for socket in inputSockets:
			originSocket = self.getOriginSocketWithCache(socket)
			socketPairs.append((socket, originSocket))
		return socketPairs
	def getOriginSocketWithCache(self, socket):
		originSocket = animationTreeCache.getOriginSocket(socket)
		if originSocket is None: # -> not found in cache -> calculate again
			originSocket = getOriginSocket(socket)
			animationTreeCache.setOriginSocket(socket, originSocket) # store this in the cache now
		return originSocket
	

class AnimationNode:
	def __init__(self, node):
		self.node = node
		self.isUpdated = False
		self.input = {}
		self.output = {}
		
	def getDependencyNodeNames(self):
		dependencyNodeNames = self.getDependencyNodeNamesWithCache()
		if dependencyNodeNames is None: # -> not found in cache
			dependencyNodeNames = []
			for socket in self.node.inputs:
				if isSocketLinked(socket): dependencyNodeNames.append(getOriginSocket(socket).node.name)
			animationTreeCache.setNodeDependencies(self.node, dependencyNodeNames) # store this in the cache now
		return dependencyNodeNames
		
	def getDependencyNodeNamesWithCache(self):
		return animationTreeCache.getDependencyNodeNames(self.node)
		
	def execute(self):
		self.output = self.node.execute(self.input)
	

# setup cache object; used globally for all animation node trees
animationTreeCache = AnimationTreeCache()
		
		
		
		
# Force Cache Rebuilding Panel
##############################
		
class AnimationNodesPanel(bpy.types.Panel):
	bl_idname = "mn.panel"
	bl_label = "Animation Nodes"
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "UI"
	bl_context = "objectmode"
	
	@classmethod
	def poll(self, context):
		return len(getAnimationNodeTrees()) > 0
	
	def draw(self, context):
		layout = self.layout
		layout.operator("mn.force_full_update")
		
		
class ForceNodeTreeUpdate(bpy.types.Operator):
	bl_idname = "mn.force_full_update"
	bl_label = "Force Node Tree Update"

	def execute(self, context):
		updateAnimationTrees(treeChanged = True)
		return {'FINISHED'}
	
	
	
	
# handlers to start the update
##############################
	
@persistent
def frameChangeHandler(scene):
	updateAnimationTrees(False)
def nodePropertyChanged(self, context):
	updateAnimationTrees(False)
def nodeTreeChanged():
	updateAnimationTrees(True)
		
def updateAnimationTrees(treeChanged = True):
	try:
		if treeChanged: updateAndRebuildCache()
		else: fastUpdateUsingCache()
	except:
		if not treeChanged:
			try:
				updateAndRebuildCache()
			except BaseException as e:
				print("couldn't update")
				print(str(e))
			
def fastUpdateUsingCache():
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:		
		animationNodeTree = AnimationNodeTree(nodeTree)
		animationNodeTree.execute(rebuildDependencyCache = False)
		
def updateAndRebuildCache():
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:		
		animationNodeTree = AnimationNodeTree(nodeTree)
		animationNodeTree.execute(rebuildDependencyCache = True)
		
def getAnimationNodeTrees():
	nodeTrees = []
	for nodeTree in bpy.data.node_groups:
		if hasattr(nodeTree, "isAnimationNodeTree"):
			nodeTrees.append(nodeTree)
	return nodeTrees

	
bpy.app.handlers.frame_change_post.append(frameChangeHandler)
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)