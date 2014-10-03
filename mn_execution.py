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

bpy.types.Scene.updateAnimationTreeOnFrameChange = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Frame Change")
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
	
compiledCodeObjects = []

def updateAnimationTrees(treeChanged = True):
	global compiledCodeObjects
	if treeChanged:
		compiledCodeObjects = []
		nodeNetworks = getNodeNetworks()
		for network in nodeNetworks:
			codeString = getCodeStringToExecuteNetwork(network)
			compiledCodeObjects.append(compile(codeString, "<string>", "exec"))
	for codeObject in compiledCodeObjects:
		try: exec(codeObject)
		except BaseException as e: print(e)
		
def getCodeStringToExecuteNetwork(network):
	orderedNodes = orderNodes(network)
	for i, node in enumerate(orderedNodes):
		node.codeIndex = i
	codeLines = []
	codeLines.append("nodes = bpy.data.node_groups['" + network[0].id_data.name + "'].nodes")
	for node in orderedNodes:
		declaration = getNodeVariableName(node) + " = nodes['"+node.name+"']"
		inputDictionaryString = generateInputListString(node)
		executionCode = getNodeOutputName(node) + " = " + getNodeVariableName(node) + ".execute(" + inputDictionaryString + ")"
		codeLines.append(declaration)
		codeLines.append(executionCode)
	codeString = "\n".join(codeLines)
	return codeString
		
def generateInputListString(node):
	inputParts = []
	for socket in node.inputs:
		originSocket = getOriginSocket(socket)
		if isOtherOriginSocket(socket, originSocket):
			otherNode = originSocket.node
			part = "'" + socket.identifier + "' : " + getNodeOutputName(otherNode) + "['" + originSocket.identifier + "']"
		else:
			part = "'" + socket.identifier + "' : " + getNodeVariableName(node) + ".inputs['" + socket.identifier + "'].getValue()"
		inputParts.append(part)
	return "{ " + ", ".join(inputParts) + " }"
		
def getNodeVariableName(node):
	return "node_" + str(node.codeIndex)
def getNodeInputName(node):
	return "input_" + str(node.codeIndex)
def getNodeOutputName(node):
	return "output_" + str(node.codeIndex)
		

bpy.types.Node.isFound = bpy.props.BoolProperty(default = False)
bpy.types.Node.codeIndex = bpy.props.IntProperty()
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
	
def orderNodes(nodes):
	for node in nodes:
		node.isFound = False
	orderedNodeList = []
	for node in nodes:
		if not node.isFound:
			orderedNodeList.extend(getAllNodeDependencies(node))
			orderedNodeList.append(node)
			node.isFound = True
	return orderedNodeList

def getAllNodeDependencies(node):
	dependencies = []
	directDependencies = []
	for socket in node.inputs:
		if hasLinks(socket):
			node = socket.links[0].from_node
			if not node.isFound:
				node.isFound = True
				directDependencies.append(node)
	for node in directDependencies:
		dependencies.extend(getAllNodeDependencies(node))
	dependencies.extend(directDependencies)
	return dependencies
		
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