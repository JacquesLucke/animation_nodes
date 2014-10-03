import bpy, time
from bpy.app.handlers import persistent
from mn_utils import *

		
		
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
		scene = context.scene
		layout.label("Update when:")
		layout.prop(scene, "updateAnimationTreeOnFrameChange", text = "Frames Changes")
		layout.prop(scene, "updateAnimationTreeOnSceneUpdate", text = "Scene Updates")
		layout.prop(scene, "updateAnimationTreeOnPropertyChange", text = "Property Changes")
		
		
		
class ForceNodeTreeUpdate(bpy.types.Operator):
	bl_idname = "mn.force_full_update"
	bl_label = "Force Node Tree Update"

	def execute(self, context):
		updateAnimationTrees(treeChanged = True)
		return {'FINISHED'}
	
	
	
	
# handlers to start the update
##############################

bpy.types.Scene.updateAnimationTreeOnFrameChange = bpy.props.BoolProperty(default = False, name = "Update Animation Tree On Frame Change")
bpy.types.Scene.updateAnimationTreeOnSceneUpdate = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Scene Update")
bpy.types.Scene.updateAnimationTreeOnPropertyChange = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Property Change")
	
@persistent
def frameChangeHandler(scene):
	if scene.updateAnimationTreeOnFrameChange:
		updateAnimationTrees(False)
@persistent
def sceneUpdateHandler(scene):
	if scene.updateAnimationTreeOnSceneUpdate:
		updateAnimationTrees(False)
@persistent
def fileLoadHandler(scene):
	updateAnimationTrees(True)
def nodePropertyChanged(self, context):
	if context.scene.updateAnimationTreeOnPropertyChange:
		updateAnimationTrees(False)
def nodeTreeChanged():
	updateAnimationTrees(True)

def updateAnimationTrees(treeChanged = True):
	nodeNetworks = getNodeNetworks()
	print()
	for network in nodeNetworks:
		nodeNameList = [node.name for node in network]
		print(nodeNameList)

bpy.types.Node.isFound = bpy.props.BoolProperty(default = False)
def getNodeNetworks():
	nodeNetworks = []
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:
		nodeNetworks.extend(getNodeNetworksFromTree(nodeTree))
	return nodeNetworks
		
def getNodeNetworksFromTree(nodeTree):
	nodes = nodeTree.nodes
	for node in nodes:
		node.isFound = False
	
	networks = []
	for node in nodes:
		if not node.isFound:
			networks.append(getNodeNetworkFromNode(node))
	return networks
	
def getNodeNetworkFromNode(node):
	nodesToCheck = [node]
	network = [node]
	node.isFound = True
	while len(nodesToCheck) > 0:
		newCheckNodes = []
		for node in nodesToCheck:
			newCheckNodes.extend(getNotFoundLinkedNodes(node))
		network.extend(newCheckNodes)
		for node in newCheckNodes:
			node.isFound = True
		nodesToCheck = newCheckNodes
	return network
			

	
def getNotFoundLinkedNodes(node):
	nodes = []
	for socket in node.inputs:
		for link in socket.links:
			nodes.append(link.from_node)
	for socket in node.outputs:
		for link in socket.links:
			nodes.append(link.to_node)
	nodes = [node for node in nodes if not node.isFound]
	return nodes
		
def getAnimationNodeTrees():
	nodeTrees = []
	for nodeTree in bpy.data.node_groups:
		if hasattr(nodeTree, "isAnimationNodeTree"):
			nodeTrees.append(nodeTree)
	return nodeTrees

	
bpy.app.handlers.frame_change_post.append(frameChangeHandler)
bpy.app.handlers.scene_update_post.append(sceneUpdateHandler)
bpy.app.handlers.load_post.append(fileLoadHandler)
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)