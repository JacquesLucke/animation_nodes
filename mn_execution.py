import bpy, time
from bpy.app.handlers import persistent
from mn_utils import *



compiledCodeObjects = []
codeStrings = []

def updateAnimationTrees(treeChanged = True):
	start = time.clock()
	if treeChanged:
		rebuildNodeNetworks()
	for i, codeObject in enumerate(compiledCodeObjects):	
		try: exec(codeObject, {})
		except BaseException as e:
			rebuildNodeNetworks()
			try: exec(codeObject, {})
			except BaseException as e: print(e)
	if bpy.context.scene.printUpdateTime:
		timeSpan = time.clock() - start
		print(str(round(timeSpan, 7)) + "  -  " + str(round(1/timeSpan, 5)) + " fps")
			
			
# compile code objects
################################
subPrograms = {}	
def rebuildNodeNetworks():
	global compiledCodeObjects, subPrograms, codeStrings, idCounter
	cleanupNodeTrees()
	del compiledCodeObjects[:]
	del codeStrings[:]
	nodeNetworks = getNodeNetworks()
	normalNetworks = []
	subPrograms = {}
	idCounter = 0
	for network in nodeNetworks:
		setUniqueCodeIndexToEveryNode(network)
		networkType = getNetworkType(network)
		if networkType == "Normal": normalNetworks.append(network)
		elif networkType == "SubProgram":
			startNode = getSubProgramStartNodeOfNetwork(network)
			subPrograms[getNodeIdentifier(startNode)] = network
	for network in normalNetworks:
		codeGenerator = NetworkCodeGenerator(network)
		codeString = codeGenerator.getCode()
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
			
			
class NetworkCodeGenerator:
	def __init__(self, network):
		self.network = network
		self.functions = {}
		
	def getCode(self):
		network = self.network
		self.orderedNodes = orderNodes(network)
		mainLines = []
		mainLines.append("nodes = bpy.data.node_groups['" + network[0].id_data.name + "'].nodes")
		for node in self.orderedNodes:
			mainLines.extend(self.getNodeCodeLines(node))
		codeString = "import bpy\n\n" + "\n\n".join(self.functions.values()) + "\n\n" + "\n".join(mainLines)
		return codeString
		
	def makeFunctionCode(self, functionNetwork):
		startNode = getSubProgramStartNodeOfNetwork(functionNetwork)
		if getNodeIdentifier(startNode) not in self.functions:
			self.functions[getNodeIdentifier(startNode)] = self.getFunctionCode(functionNetwork, startNode)
	def getFunctionCode(self, functionNetwork, startNode):
		self.orderedNodes = orderNodes(functionNetwork)
		mainLines = []
		mainLines.append("def " + getNodeFunctionName(startNode) + "(" + getNodeOutputName(startNode) + "):")
		mainLines.append("    global nodes")
		for node in self.orderedNodes:
			if node != startNode:
				codeLines = self.getNodeCodeLines(node)
				self.setIndentationOnEveryLine(codeLines)
				mainLines.extend(codeLines)
		functionString = "\n".join(mainLines)
		return functionString
	def setIndentationOnEveryLine(self, codeLines):
		for i, line in enumerate(codeLines):
			codeLines[i] = "    " + line
		
	def getNodeCodeLines(self, node):
		codeLines = []
		if isExecuteableNode(node):
			codeLines.append(getNodeDeclarationString(node))
			codeLines.append(getNodeExecutionString(node))
		elif isSubProgramNode(node):
			codeLines.append(getNodeDeclarationString(node))
			codeLines.append(getNodeInputName(node) + " = " + generateInputListString(node, ignoreSocketNames = "Sub-Program"))
			startNode = getCorrespondingStartNode(node)
			if startNode is not None:
				codeLines.append("for i in range(" + getNodeInputName(node) + "['Amount']):")
				codeLines.append("    " + getNodeInputName(node) + "['Index'] = i")
				codeLines.append("    " + getNodeFunctionName(startNode) + "(" + getNodeInputName(node) + ")")
				self.makeFunctionCode(subPrograms[getNodeIdentifier(startNode)])
			codeLines.append(getNodeOutputName(node) + " = " + getNodeInputName(node))
		return codeLines		
		
def getNodeDeclarationString(node):
	return getNodeVariableName(node) + " = nodes['"+node.name+"']"
def getNodeExecutionString(node):
	return getNodeOutputName(node) + " = " + getNodeVariableName(node) + ".execute(" + generateInputListString(node) + ")"
	
def getCorrespondingStartNode(node):
	return node.getStartNode()
		
idCounter = 0
bpy.types.Node.codeIndex = bpy.props.IntProperty()
def setUniqueCodeIndexToEveryNode(nodes):
	global idCounter
	for node in nodes:
		node.codeIndex = idCounter
		idCounter += 1
		
def isExecuteableNode(node):
	return hasattr(node, "execute")
def isSubProgramNode(node):
	return node.bl_idname == "SubProgramNode"
		
def generateInputListString(node, ignoreSocketNames = []):
	inputParts = []
	for socket in node.inputs:
		if socket.name not in ignoreSocketNames:
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
	nodes.extend(getNotFoundInputNodes(node))
	nodes.extend(getNotFoundOutputNodes(node))
	return nodes
def getNotFoundInputNodes(node):
	nodes = []
	for socket in node.inputs:
		for link in socket.links:
			fromNode = link.from_node
			if not fromNode.isFound:
				nodes.append(fromNode)
				fromNode.isFound = True
	return nodes
def getNotFoundOutputNodes(node):
	nodes = []
	for socket in node.outputs:
		for link in socket.links:
			toNode = link.to_node
			if not toNode.isFound:
				nodes.append(toNode)
				toNode.isFound = True
	return nodes
	
bpy.types.Node.isFound = bpy.props.BoolProperty(default = False)
def resetNodeFoundAttributes(nodes):
	for node in nodes: node.isFound = False
		
	

# order nodes (network) to possible execution sequence
######################################################
	
def orderNodes(nodes):
	preOrderedList = []
	for node in nodes:
		preOrderedList.extend(getAllNodeDependencies(node))
		preOrderedList.append(node)
	
	orderedList = []
	for node in preOrderedList:
		if node not in orderedList and node in nodes: orderedList.append(node)
	return orderedList

def getAllNodeDependencies(node):
	dependencies = []
	directDependencies = getDirectDependencies(node)
	for directDependency in directDependencies:
		dependencies.extend(getAllNodeDependencies(directDependency))
	dependencies.extend(directDependencies)
	return dependencies
	
def getDirectDependencies(node):
	directDependencies = []
	for socket in node.inputs:
		if hasLinks(socket):
			node = socket.links[0].from_node
			directDependencies.append(node)
	return directDependencies
	


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
		if toSocket.node.type == "REROUTE" or fromSocket.node.type == "REROUTE" or not isSocketLinked(toSocket):
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
		layout.operator("mn.print_node_tree_execution_string")
		scene = context.scene
		layout.label("Update when:")
		layout.prop(scene, "updateAnimationTreeOnFrameChange", text = "Frames Changes")
		layout.prop(scene, "updateAnimationTreeOnSceneUpdate", text = "Scene Updates")
		layout.prop(scene, "updateAnimationTreeOnPropertyChange", text = "Property Changes")
		layout.prop(scene, "printUpdateTime", text = "Print Update Time")
		
		
		
class ForceNodeTreeUpdate(bpy.types.Operator):
	bl_idname = "mn.force_full_update"
	bl_label = "Force Node Tree Update"

	def execute(self, context):
		updateAnimationTrees(treeChanged = True)
		return {'FINISHED'}
		
class PrintNodeTreeExecutionStrings(bpy.types.Operator):
	bl_idname = "mn.print_node_tree_execution_string"
	bl_label = "Print Node Tree Code"

	def execute(self, context):
		print()
		for codeString in codeStrings:
			print(codeString)
			print()
		return {'FINISHED'}
	
	
		
# handlers to start the update
##############################

bpy.types.Scene.updateAnimationTreeOnFrameChange = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Frame Change")
bpy.types.Scene.updateAnimationTreeOnSceneUpdate = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Scene Update")
bpy.types.Scene.updateAnimationTreeOnPropertyChange = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Property Change")

bpy.types.Scene.printUpdateTime = bpy.props.BoolProperty(default = False, name = "Print Update Time")
	
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