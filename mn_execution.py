import bpy, time
from bpy.app.handlers import persistent
from mn_utils import *



compiledCodeObjects = []
codeStrings = []

def updateAnimationTrees(treeChanged = True):
	if treeChanged:
		rebuildNodeNetworks()
	for i, codeObject in enumerate(compiledCodeObjects):
		print(codeStrings[i])
		file = open("C:\\Users\\Jacques Lucke\\Documents\\test.py", "w")
		file.write(codeStrings[i])
		file.close()
		exec(codeObject)
		#try: exec(codeObject)
		#except BaseException as e: print(e)
			#rebuildNodeNetworks()
			#try: exec(codeObject)
			#except BaseException as e: print(e)
			
			
# compile code objects
################################
subPrograms = {}	
def rebuildNodeNetworks():
	global compiledCodeObjects, subPrograms, codeStrings
	cleanupNodeTrees()
	del compiledCodeObjects[:]
	del codeStrings[:]
	nodeNetworks = getNodeNetworks()
	normalNetworks = []
	subPrograms = {}
	print()
	for network in nodeNetworks:
		setUniqueCodeIndexToEveryNode(network)
		networkType = getNetworkType(network)
		print(networkType)
		if networkType == "Normal": normalNetworks.append(network)
		elif networkType == "SubProgram":
			startNode = getSubProgramStartNodeOfNetwork(network)
			subPrograms[getNodeIdentifier(startNode)] = network
	for network in normalNetworks:
		codeGenerator = NormalNetworkStringGenerator(network)
		codeString = codeGenerator.getCodeString()
		#print(codeString)
		codeStrings.append(codeString)
		compiledCodeObjects.append(compile(codeString, "<string>", "exec"))
		
def getNetworkType(network):
	subProgramAmount = 0
	for node in network:
		if node.bl_idname == "SubProgramStartNode":
			subProgramAmount += 1
	if subProgramAmount == 0: return "Normal"
	elif subProgramAmount == 1: return "SubProgram"
	return "Invalid"
def getSubProgramStartNodeOfNetwork(network):
	for node in network:
		if node.bl_idname == "SubProgramStartNode":
			return node
			
class NormalNetworkStringGenerator:
	def __init__(self, network):
		self.network = network
		self.functions = []
		self.codeLines = []
		self.orderedNodes = []
	def getCodeString(self):
		network = self.network
		self.orderedNodes = orderNodes(network)
		codeLines = []
		codeLines.append("nodes = bpy.data.node_groups['" + network[0].id_data.name + "'].nodes")
		for node in self.orderedNodes:
			if isExecuteableNode(node):
				codeLines.append(getNodeDeclarationString(node))
				codeLines.append(getNodeExecutionString(node))
			if isSubProgramNode(node):
				codeLines.append(getNodeDeclarationString(node))
				codeLines.append(getNodeInputName(node) + " = " + generateInputListStringForSubProgram(node))
				codeLines.append("for i in range(" + getNodeInputName(node) + "['Amount']):")
				codeLines.append("    " + getNodeInputName(node) + "['Index'] = i")
				codeLines.append("    " + getNodeFunctionName(node.inputs[0].links[0].from_node) + "(" + getNodeInputName(node) + ")")
				codeLines.append(getNodeOutputName(node) + " = " + getNodeInputName(node))
				subProgramNetworkStringGenerator = SubProgramNetworkStringGenerator(subPrograms[getNodeIdentifier(node.inputs[0].links[0].from_node)])
				self.functions.append(subProgramNetworkStringGenerator.getCodeString())
		codeString = "import bpy\n" + "\n".join(self.functions) + "\n\n" + "\n".join(codeLines)
		return codeString
		
def getNodeDeclarationString(node):
	return getNodeVariableName(node) + " = nodes['"+node.name+"']"
def getNodeExecutionString(node):
	return getNodeOutputName(node) + " = " + getNodeVariableName(node) + ".execute(" + generateInputListString(node) + ")"
		
		
class SubProgramNetworkStringGenerator:
	def __init__(self, network):
		self.network = network
		self.functions = []
		self.orderedNodes = []
	def getCodeString(self):
		network = self.network
		startNode = getSubProgramStartNodeOfNetwork(network)
		self.orderedNodes = orderNodes(network)
		codeLines = []
		codeLines.append("def " + getNodeFunctionName(startNode) + "(" + getNodeOutputName(startNode) + "):")
		codeLines.append("    global nodes")
		for node in self.orderedNodes:
			if node != startNode:
				if isExecuteableNode(node):
					codeLines.append("    " + getNodeDeclarationString(node))
					codeLines.append("    " + getNodeExecutionString(node))
				if isSubProgramNode(node):
					codeLines.append("    " + getNodeDeclarationString(node))
					codeLines.append("    " + getNodeInputName(node) + " = " + generateInputListStringForSubProgram(node))
					codeLines.append("    for i in range(" + getNodeInputName(node) + "['Amount']):")
					codeLines.append("        " + getNodeInputName(node) + "['Index'] = i")
					codeLines.append("        " + getNodeFunctionName(node.inputs[0].links[0].from_node) + "(" + getNodeInputName(node) + ")")
					codeLines.append("    " + getNodeOutputName(node) + " = " + getNodeInputName(node))
					subProgramNetworkStringGenerator = SubProgramNetworkStringGenerator(subPrograms[getNodeIdentifier(node.inputs[0].links[0].from_node)])
					self.functions.append(subProgramNetworkStringGenerator.getCodeString())
		codeString = "\n".join(self.functions) + "\n\n" + "\n".join(codeLines)
		return codeString
		
		
idCounter = 0	
def setUniqueCodeIndexToEveryNode(nodes):
	global idCounter
	for node in nodes:
		node.codeIndex = idCounter
		idCounter += 1
		
def isExecuteableNode(node):
	return hasattr(node, "execute")
def isSubProgramNode(node):
	return node.bl_idname == "SubProgramNode"

		
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
	
def generateInputListStringForSubProgram(node):
	inputParts = []
	for i, socket in enumerate(node.inputs):
		if i >= 1:
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
def getNodeFunctionName(node):
	return getNodeVariableName(node) + "_" + "Function"
		

# get node networks (groups of connected nodes)
###############################################
		
def getNodeNetworks():
	nodeNetworks = []
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:
		nodeNetworks.extend(getNodeNetworksFromTree(nodeTree))
	return nodeNetworks
	
def getAnimationNodeTrees():
	nodeTrees = []
	for nodeTree in bpy.data.node_groups:
		if hasattr(nodeTree, "isAnimationNodeTree"):
			nodeTrees.append(nodeTree)
	return nodeTrees
		
def getNodeNetworksFromTree(nodeTree):
	nodes = nodeTree.nodes
	resetNodeFoundAttributes(nodes)
	
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
		linkedNodes = []
		for node in nodesToCheck:
			linkedNodes.extend(getLinkedButNotFoundNodes(node))
		network.extend(linkedNodes)
		setNodesAsFound(linkedNodes)
		nodesToCheck = linkedNodes
	return network
	
def setNodesAsFound(nodes):
	for node in nodes: node.isFound = True
	
def getLinkedButNotFoundNodes(node):
	nodes = []
	for socket in node.inputs:
		for link in socket.links:
			if not isSystemLink(link) and link.from_node not in nodes:
				nodes.append(link.from_node)
	for socket in node.outputs:
		for link in socket.links:
			if not isSystemLink(link) and link.from_node not in nodes:
				nodes.append(link.to_node)
	nodes = sortOutAlreadyFoundNodes(nodes)
	return nodes
	
def sortOutAlreadyFoundNodes(nodes):
	return [node for node in nodes if not node.isFound]
def isSystemLink(link):
	return link.to_socket.bl_idname == "SubProgramSocket"
	

# order nodes (network) to possible execution sequence
######################################################
	
def orderNodes(nodes):
	resetNodeFoundAttributes(nodes)
	orderedNodeList = []
	for node in nodes:
		if not node.isFound:
			orderedNodeList.extend(getAllNodeDependencies(node))
			orderedNodeList.append(node)
			node.isFound = True
	return orderedNodeList

def getAllNodeDependencies(node):
	dependencies = []
	directDependencies = getNotFoundDirectDependencies(node)
	for directDependency in directDependencies:
		dependencies.extend(getAllNodeDependencies(directDependency))
	dependencies.extend(directDependencies)
	return dependencies
	
def getNotFoundDirectDependencies(node):
	directDependencies = []
	for socket in node.inputs:
		if hasLinks(socket):
			node = socket.links[0].from_node
			if not node.isFound:
				node.isFound = True
				directDependencies.append(node)
	return directDependencies
	
def resetNodeFoundAttributes(nodes):
	for node in nodes: node.isFound = False
		
	
bpy.types.Node.isFound = bpy.props.BoolProperty(default = False)
bpy.types.Node.codeIndex = bpy.props.IntProperty()


# cleanup of node trees
################################

convertableTypes = [("Float", "Integer", "ToIntegerConversion"),
					("Float", "String", "ToStringConversion"),
					("Integer", "String", "ToStringConversion")]
		
def cleanupNodeTrees():
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:
		cleanupNodeTree(nodeTree)
def cleanupNodeTree(nodeTree):
	links = nodeTree.links
	for link in links:
		toSocket = link.to_socket
		fromSocket = link.from_socket
		if toSocket.node.type == "REROUTE" or not isSocketLinked(toSocket):
			continue
		if fromSocket.dataType not in toSocket.allowedInputTypes and toSocket.allowedInputTypes[0] != "all":
			handleNotAllowedLink(nodeTree, link, fromSocket, toSocket)
def handleNotAllowedLink(nodeTree, link, fromSocket, toSocket):
	fromType = fromSocket.dataType
	toType = toSocket.dataType
	nodeTree.links.remove(link)
	for (t1, t2, nodeType) in convertableTypes:
		if fromType == t1 and toType == t2: insertConversionNode(nodeTree, nodeType, link, fromSocket, toSocket)
def insertConversionNode(nodeTree, nodeType, link, fromSocket, toSocket):
	node = nodeTree.nodes.new(nodeType)
	node.hide = True
	node.select = False
	x1, y1 = toSocket.node.location
	x2, y2 = list(fromSocket.node.location)
	node.location = [(x1+x2)/2+20, (y1+y2)/2-50]
	nodeTree.links.new(node.inputs[0], fromSocket)
	nodeTree.links.new(toSocket, node.outputs[0])

		
		
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

	
bpy.app.handlers.frame_change_post.append(frameChangeHandler)
bpy.app.handlers.scene_update_post.append(sceneUpdateHandler)
bpy.app.handlers.load_post.append(fileLoadHandler)
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)