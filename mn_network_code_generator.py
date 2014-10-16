import bpy
from mn_utils import *

normalNetworks = []
subNetworks = {}	

def getAllNetworkCodeStrings():
	global subNetworks
	networkStrings = []
	cleanupNodeTrees()
	nodeNetworks = getNodeNetworks()
	sortNetworks(nodeNetworks)
	for network in normalNetworks:
		codeGenerator = NetworkCodeGenerator(network)
		networkStrings.append(codeGenerator.getCode())
	return networkStrings
	
def sortNetworks(nodeNetworks):
	global normalNetworks, subNetworks, idCounter
	normalNetworks = []
	subNetworks = {}
	idCounter = 0
	for network in nodeNetworks:
		setUniqueCodeIndexToEveryNode(network)
		networkType = getNetworkType(network)
		if networkType == "Normal": normalNetworks.append(network)
		elif networkType == "Loop":
			startNode = getSubProgramStartNode(network)
			subNetworks[getNodeIdentifier(startNode)] = network
		
def getNetworkType(network):
	loopStarterAmount = 0
	for node in network:
		if node.bl_idname == "mn_LoopStartNode" or node.bl_idname == "mn_EnumerateObjectsStartNode":
			loopStarterAmount += 1
	if loopStarterAmount == 0: return "Normal"
	elif loopStarterAmount == 1: return "Loop"
	return "Invalid"
def getSubProgramStartNode(network):
	for node in network:
		if node.bl_idname == "mn_LoopStartNode" or node.bl_idname == "mn_EnumerateObjectsStartNode":
			return node
			
idCounter = 0
bpy.types.Node.codeIndex = bpy.props.IntProperty()
def setUniqueCodeIndexToEveryNode(nodes):
	global idCounter
	for node in nodes:
		node.codeIndex = idCounter
		idCounter += 1
		

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
			nodeTree.use_fake_user = True
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


# cleanup of node trees
################################

convertableTypes = [("Float", "Integer", "mn_ToIntegerConversion"),
					("Float", "String", "mn_ToStringConversion"),
					("Integer", "String", "mn_ToStringConversion"),
					("Float", "Vector", "mn_CombineVector"),
					("Integer", "Vector", "mn_CombineVector")]
		
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
	
	
	
# network code generator class
########################################

class NetworkCodeGenerator:
	def __init__(self, network):
		self.network = network
		self.functions = {}
		self.neededSocketReferences = []
		self.allNodesInTree = []
		
	def getCode(self):
		mainCode = self.getMainCode()
		
		codeParts = []
		codeParts.append("import bpy, time")
		codeParts.append("nodes = bpy.data.node_groups['" + self.network[0].id_data.name + "'].nodes")
		codeParts.append(self.getNodeReferencingCode())
		codeParts.append(self.getSocketReferencingCode())
		codeParts.append(self.getTimerDefinitions())
		codeParts.append(self.getFunctionsCode())
		codeParts.append(mainCode)
		codeParts.append(self.getCodeToPrintProfilingResult())
		return "\n".join(codeParts)
		
	def getMainCode(self):
		self.allNodesInTree.extend(self.network)
		self.orderedNodes = orderNodes(self.network)
		codeLines = []
		for node in self.orderedNodes:
			codeLines.extend(self.getNodeCodeLines(node))
		return "\n".join(codeLines)
		
	def makeFunctionCode(self, functionNetwork):
		startNode = getSubProgramStartNode(functionNetwork)
		if getNodeIdentifier(startNode) not in self.functions:
			self.functions[getNodeIdentifier(startNode)] = self.getFunctionCode(functionNetwork, startNode)
	def getFunctionCode(self, functionNetwork, startNode):
		self.allNodesInTree.extend(functionNetwork)
		self.orderedNodes = orderNodes(functionNetwork)
		mainLines = []
		mainLines.append("def " + getNodeFunctionName(startNode) + "(" + getNodeOutputName(startNode) + "):")
		mainLines.append("    global nodes")
		mainLines.append("    " + self.getTimerGlobalList(functionNetwork))
		for node in self.orderedNodes:
			if node != startNode:
				codeLines = self.getNodeCodeLines(node)
				self.setIndentationOnEveryLine(codeLines)
				mainLines.extend(codeLines)
		if bpy.context.scene.nodeExecutionProfiling: mainLines.append("    globals().update(locals())")
		functionString = "\n".join(mainLines)
		return functionString
	def setIndentationOnEveryLine(self, codeLines):
		for i, line in enumerate(codeLines):
			codeLines[i] = "    " + line
			
	def getFunctionsCode(self):
		return "\n\n".join(self.functions.values())
		
	def getNodeCodeLines(self, node):
		codeLines = []
		if isExecuteableNode(node):
			codeLines.extend(self.getExecutableNodeCode(node))
		elif isLoopNode(node):
			codeLines.extend(self.getLoopNodeCode(node))
		elif isEnumerateObjectsNode(node):
			codeLines.extend(self.getEnumerateObjectsNodeCode(node))
		return codeLines		
		
	def getExecutableNodeCode(self, node):
		codeLines = []
		if bpy.context.scene.nodeExecutionProfiling: codeLines.append(getNodeTimerStartName(node) + " = time.clock()")
		codeLines.append(self.getNodeExecutionString(node))
		if bpy.context.scene.nodeExecutionProfiling: codeLines.append(getNodeTimerName(node) + " += time.clock() - " + getNodeTimerStartName(node))
		return codeLines
	def getLoopNodeCode(self, node):
		codeLines = []
		codeLines.append(getNodeInputName(node) + " = " + self.generateInputListString(node))
		startNode = getCorrespondingStartNode(node)
		if startNode is not None:
			codeLines.append("for i in range(" + getNodeInputName(node) + "['Amount']):")
			codeLines.append("    " + getNodeInputName(node) + "['Index'] = i")
			codeLines.append("    " + getNodeFunctionName(startNode) + "(" + getNodeInputName(node) + ")")
			self.makeFunctionCode(subNetworks[getNodeIdentifier(startNode)])
		codeLines.append(getNodeOutputName(node) + " = " + getNodeInputName(node))
		return codeLines
	def getEnumerateObjectsNodeCode(self, node):
		codeLines = []
		inputName = getNodeInputName(node)
		codeLines.append(inputName + " = " + self.generateInputListString(node))
		codeLines.append(inputName + "['List Length'] = len("+ inputName + "['Objects'])")
		startNode = getCorrespondingStartNode(node)
		if startNode is not None:
			codeLines.append("if " + getNodeVariableName(node) + ".executeLoop:")
			codeLines.append("    for i, object in enumerate(" + inputName + "['Objects']):")
			codeLines.append("        " + inputName + "['Index'] = i")
			codeLines.append("        " + inputName + "['Object'] = object")
			codeLines.append("        " + getNodeFunctionName(startNode) + "(" + inputName + ")")
			self.makeFunctionCode(subNetworks[getNodeIdentifier(startNode)])
		codeLines.append(getNodeOutputName(node) + " = " + inputName)
		return codeLines
		
	def getTimerDefinitions(self):
		if bpy.context.scene.nodeExecutionProfiling:
			codeLines = []
			for node in self.allNodesInTree:
				codeLines.append(getNodeTimerName(node) + " = 0")
			return "\n" + "\n".join(codeLines) + "\n"
		return ""
	def getTimerGlobalList(self, network):
		if bpy.context.scene.nodeExecutionProfiling:
			nodeTimerNames = []
			for node in network:
				nodeTimerNames.append(getNodeTimerName(node))
			return "global " + ", ".join(nodeTimerNames)
		return ""
		
	def getCodeToPrintProfilingResult(self):
		if bpy.context.scene.nodeExecutionProfiling:
			codeLines = []
			codeLines.append("print('----------  Profiling  ----------')")
			for node in self.allNodesInTree:
				codeLines.append("print('" + node.name + "')")
				codeLines.append("print('  ' + str(round(" + getNodeTimerName(node) + ", 5)) + ' s')")
			return "\n" + "\n".join(codeLines)
		return ""
		
	def getNodeReferencingCode(self):
		codeLines = []
		for node in self.allNodesInTree:
			codeLines.append(self.getNodeDeclarationString(node))
		return "\n".join(codeLines)
		
	def getSocketReferencingCode(self):
		codeLines = []
		for socket in self.neededSocketReferences:
			codeLines.append(self.getSocketDeclarationString(socket))
		return "\n".join(codeLines)
	

	def generateInputListString(self, node):
		inputParts = []
		useFastMethod = usesFastCall(node)
		inputSocketNames = None
		if useFastMethod: inputSocketNames = node.getInputSocketNames()
		for socket in node.inputs:
			originSocket = getOriginSocket(socket)
			if isOtherOriginSocket(socket, originSocket):
				inputParts.append(self.getInputPartFromOtherNode(socket, originSocket, useFastMethod, inputSocketNames))
			else:
				self.neededSocketReferences.append(socket)
				inputParts.append(self.getInputPartFromSameNode(socket, useFastMethod, inputSocketNames))
		return self.joinInputParts(inputParts, useFastMethod)
			
	def joinInputParts(self, inputParts, useFastMethod):
		if useFastMethod:
			return ", ".join(inputParts)
		else:
			return "{ " + ", ".join(inputParts) + " }"
	def getInputPartFromSameNode(self, socket, useFastMethod, inputSocketNames):
		if useFastMethod:
			return inputSocketNames[socket.identifier] + " = " + getInputSocketVariableName(socket)
		else:
			return "'" + socket.identifier + "' : " + getInputSocketVariableName(socket)
	def getInputPartFromOtherNode(self, socket, originSocket, useFastMethod, inputSocketNames):
		originNode = originSocket.node
		originUsesFastMethod = usesFastCall(originNode)
		outputSocketNames = None
		if originUsesFastMethod: 
			outputSocketNames = originNode.getOutputSocketNames()
		return self.getInputPartStart(socket, useFastMethod, inputSocketNames) + self.getInputPartEnd(originNode, originSocket, originUsesFastMethod, outputSocketNames)	
	def getInputPartStart(self, socket, useFastMethod, inputSocketNames):
		if useFastMethod:
			return inputSocketNames[socket.identifier] + " = "
		else:
			return "'" + socket.identifier + "' : "
	def getInputPartEnd(self, originNode, originSocket, originUsesFastMethod, outputSocketNames):
		if originUsesFastMethod:
			return getNodeOutputName(originNode) + "_" + outputSocketNames[originSocket.identifier]
		else:
			return getNodeOutputName(originNode) + "['" + originSocket.identifier + "']"
		
		
		
	def getNodeDeclarationString(self, node):
		return getNodeVariableName(node) + " = nodes['"+node.name+"']"
	def getSocketDeclarationString(self, socket):
		return getInputSocketVariableName(socket) + " = " + getNodeVariableName(socket.node) + ".inputs['" + socket.identifier + "'].getValue()"
	def getNodeExecutionString(self, node):
		return getNodeOutputString(node) + " = " + getNodeVariableName(node) + ".execute(" + self.generateInputListString(node) + ")"

def getNodeOutputString(node):
	if usesFastCall(node):
		outputSocketNames = node.getOutputSocketNames()
		if len(outputSocketNames) != len(node.outputs): raise Exception()
		outputParts = []
		for socket in node.outputs:
			outputParts.append(getNodeOutputName(node) + "_" + outputSocketNames[socket.identifier])
		return ", ".join(outputParts)
	else:
		return getNodeOutputName(node)
	
def getCorrespondingStartNode(node):
	return node.getStartNode()
		
def isExecuteableNode(node):
	return hasattr(node, "execute")
def isLoopNode(node):
	return node.bl_idname == "mn_LoopNode"
def isEnumerateObjectsNode(node):
	return node.bl_idname == "mn_EnumerateObjectsNode"
	
def usesFastCall(node):
	if hasattr(node, "getInputSocketNames"):
		if hasattr(node, "getOutputSocketNames"): return True
		else: raise Exception()
	if hasattr(node, "getOutputSocketNames"): raise Exception()
	return False
		
def getNodeVariableName(node):
	return "node_" + str(node.codeIndex)
def getNodeInputName(node):
	return "input_" + str(node.codeIndex)
def getNodeOutputName(node):
	return "output_" + str(node.codeIndex)
def getNodeFunctionName(node):
	return getNodeVariableName(node) + "_" + "Function"
def getNodeTimerStartName(node):
	return "timer_start_" + str(node.codeIndex)
def getNodeTimerName(node):
	return "timer_" + str(node.codeIndex)
def getInputSocketVariableName(socket):
	node = socket.node
	return getNodeVariableName(node) + "_socketvalue_" + str(node.inputs.find(socket.name))
	
	
	
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