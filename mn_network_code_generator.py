import bpy, time
from mn_utils import *

normalNetworks = []
subNetworks = {}
invalidNetworks = []
useProfiling = False

def getAllNetworkCodeStrings():
	global subNetworks, invalidNetworks, useProfiling
	useProfiling = bpy.context.scene.mn_settings.developer.executionProfiling
	networkStrings = []
	clearSocketConnections()
	cleanupNodeTrees()
	nodeNetworks = getNodeNetworks()
	sortNetworks(nodeNetworks)
	if len(invalidNetworks) > 0:
		print("invalid node tree")
		return []
	for network in normalNetworks:
		codeGenerator = NetworkCodeGenerator(network)
		networkStrings.append(codeGenerator.getCode())
	clearSocketConnections()
	return networkStrings
	
def sortNetworks(nodeNetworks):
	global normalNetworks, subNetworks, invalidNetworks, idCounter
	normalNetworks = []
	subNetworks = {}
	invalidNetworks = []
	idCounter = 0
	for network in nodeNetworks:
		setUniqueCodeIndexToEveryNode(network)
		networkType = getNetworkType(network)
		if networkType == "Normal": normalNetworks.append(network)
		elif networkType == "Loop":
			startNode = getSubProgramStartNode(network)
			subNetworks[getNodeIdentifier(startNode)] = network
		elif networkType == "Invalid": invalidNetworks.append(network)
		
def getNetworkType(network):
	loopStarterAmount = 0
	for node in network:
		if node.bl_idname == "mn_ForLoopStartNode":
			loopStarterAmount += 1
	if loopStarterAmount == 0: return "Normal"
	elif loopStarterAmount == 1: return "Loop"
	return "Invalid"
def getSubProgramStartNode(network):
	for node in network:
		if node.bl_idname == "mn_ForLoopStartNode":
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
		originSocket = getDataOriginSocket(socket)
		if originSocket is not None:
			fromNode = originSocket.node
			if not fromNode.isFound:
				nodes.append(fromNode)
				fromNode.isFound = True
	return nodes
def getNotFoundOutputNodes(node):
	nodes = []
	for socket in node.outputs:
		connectedSockets = getSocketsFromOutputSocket(socket)
		for toSocket in connectedSockets:
			toNode = toSocket.node
			if not toNode.isFound:
				nodes.append(toNode)
				toNode.isFound = True
	return nodes
	
bpy.types.Node.isFound = bpy.props.BoolProperty(default = False)
def resetNodeFoundAttributes(nodes):
	for node in nodes: node.isFound = False	


	
	
# network code generator class
########################################

class NetworkCodeGenerator:
	def __init__(self, network):
		self.network = network
		self.modules = set(["bpy", "time"])
		self.functions = {}
		self.neededSocketReferences = []
		self.allNodesInTree = []
		self.executeNodes = []
		self.outputUseNodes = []
		
	def getCode(self):
		mainCode = self.getMainCode()
		
		codeParts = []
		codeParts.append("import " + ", ".join(self.modules))
		codeParts.append("nodes = bpy.data.node_groups['" + self.network[0].id_data.name + "'].nodes")
		codeParts.append(self.getNodeReferencingCode())
		codeParts.append(self.getNodeExecuteReferencingCode())
		codeParts.append(self.getSocketReferencingCode())
		codeParts.append(self.getOutputUseDeclarationCode())
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
		
	def makeLoopCode(self, loopNetwork):
		startNode = getSubProgramStartNode(loopNetwork)
		if getNodeIdentifier(startNode) not in self.functions:
			self.functions[getNodeIdentifier(startNode)] = self.getLoopCode(loopNetwork, startNode)
	def getLoopCode(self, loopNetwork, startNode):
		self.allNodesInTree.extend(loopNetwork)
		self.orderedNodes = orderNodes(loopNetwork)
		mainLines = []
		mainLines.append("def " + getNodeFunctionName(startNode) + "(" + getNodeOutputName(startNode) + "):")
		mainLines.append("    global nodes")
		mainLines.append("    " + self.getTimerGlobalList(loopNetwork))
		for node in self.orderedNodes:
			if node != startNode:
				codeLines = self.getNodeCodeLines(node)
				self.setIndentationOnEveryLine(codeLines)
				mainLines.extend(codeLines)
		if useProfiling: mainLines.append("    globals().update(locals())")
		functionString = "\n".join(mainLines)
		return functionString
	def setIndentationOnEveryLine(self, codeLines):
		for i, line in enumerate(codeLines):
			codeLines[i] = "    " + line
			
	def getFunctionsCode(self):
		return "\n\n".join(self.functions.values())
		
	def getNodeCodeLines(self, node):
		codeLines = []
		if isExecuteableNode(node) or isInLineNode(node):
			codeLines.extend(self.getExecutableNodeCode(node))
		elif isForLoopNode(node):
			codeLines.extend(self.getForLoopNodeCode(node))
		return codeLines		
		
	def getExecutableNodeCode(self, node):
		codeLines = []
		if useProfiling: codeLines.append(getNodeTimerStartName(node) + " = time.clock()")
		codeLines.extend(self.getNodeExecutionLines(node))
		if useProfiling: codeLines.append(getNodeTimerName(node) + " += time.clock() - " + getNodeTimerStartName(node))
		return codeLines
	def getForLoopNodeCode(self, node):
		codeLines = []
		codeLines.append(getNodeInputName(node) + " = " + self.generateInputListString(node))
		startNode = getCorrespondingStartNode(node)
		if startNode is not None:
			loopHeader = self.getForLoopHeader(node, startNode)
			enumeratedObjectsLine = self.getForLoopObjectsCodeLine(node, startNode)
			codeLines.append(loopHeader)
			codeLines.append("    " + enumeratedObjectsLine)
			codeLines.append("    " + getNodeInputName(node) + "['Index'] = i")
			codeLines.append("    " + getNodeFunctionName(startNode) + "(" + getNodeInputName(node) + ")")
			self.makeLoopCode(subNetworks[getNodeIdentifier(startNode)])
		codeLines.append(getNodeOutputName(node) + " = " + getNodeInputName(node))
		return codeLines
	def getForLoopHeader(self, node, startNode):
		fromListSockets = startNode.getSocketDescriptions()[0]
		if len(fromListSockets) == 0: return "for i in range(" + getNodeInputName(node) + "['Amount']):"
		codeParts = []
		codeParts.append("for i, (")
		variableNames = []
		for socket in fromListSockets:
			variableNames.append(socket.identifier)
		codeParts.append(", ".join(variableNames))
		codeParts.append(") in enumerate(zip(")
		listVariables = []
		for socket in fromListSockets:
			listVariables.append(getNodeInputName(node) + "['" + socket.identifier + "list']")
		codeParts.append(", ".join(listVariables))
		codeParts.append(")):")
		return "".join(codeParts)
	def getForLoopObjectsCodeLine(self, node, startNode):
		fromListSockets = startNode.getSocketDescriptions()[0]
		if len(fromListSockets) == 0: return ""
		codeParts = []
		
		listVariables = []
		for socket in fromListSockets:
			listVariables.append(getNodeInputName(node) + "['" + socket.identifier + "']")
		codeParts.append(", ".join(listVariables))
		codeParts.append(" = ")
		
		variableNames = []
		for socket in fromListSockets:
			variableNames.append(socket.identifier)
		codeParts.append(", ".join(variableNames))
		
		return "".join(codeParts)
		
	def getTimerDefinitions(self):
		if useProfiling:
			codeLines = []
			for node in self.allNodesInTree:
				codeLines.append(getNodeTimerName(node) + " = 0")
			return "\n" + "\n".join(codeLines) + "\n"
		return ""
	def getTimerGlobalList(self, network):
		if useProfiling:
			nodeTimerNames = []
			for node in network:
				nodeTimerNames.append(getNodeTimerName(node))
			return "global " + ", ".join(nodeTimerNames)
		return ""
		
	def getCodeToPrintProfilingResult(self):
		if useProfiling:
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
		
	def getNodeExecuteReferencingCode(self):
		codeLines = []
		for node in self.executeNodes:
			codeLines.append(self.getNodeFunctionDeclarationString(node))
		return "\n".join(codeLines)
		
	def getSocketReferencingCode(self):
		codeLines = []
		for socket in self.neededSocketReferences:
			codeLines.append(self.getSocketDeclarationString(socket))
		return "\n".join(codeLines)
		
	def getOutputUseDeclarationCode(self):
		codeLines = []
		for node in self.outputUseNodes:
			codeLines.append(getNodeOutputUseName(node) + " = " + getOutputUseDictionaryCode(node))
		return "\n".join(codeLines)

	def generateInputListString(self, node):
		inputParts = []
		useFastMethod = usesFastCall(node)
		inputSocketNames = None
		if useFastMethod: inputSocketNames = node.getInputSocketNames()
		for socket in node.inputs:
			originSocket = getDataOriginSocket(socket)
			if originSocket is not None:
				inputParts.append(self.getInputPartFromOtherNode(socket, originSocket, useFastMethod, inputSocketNames))
			else:
				self.neededSocketReferences.append(socket)
				inputParts.append(self.getInputPartFromSameNode(socket, useFastMethod, inputSocketNames))
		if usesOutputUseParameter(node):
			self.outputUseNodes.append(node)
			return node.outputUseParameterName + " = " + getNodeOutputUseName(node) + ", " + self.joinInputParts(inputParts, useFastMethod)
		else:
			return self.joinInputParts(inputParts, useFastMethod)
			
	def joinInputParts(self, inputParts, useFastMethod):
		if useFastMethod:
			return ", ".join(inputParts)
		else:
			return "{ " + ", ".join(inputParts) + " }"
	def getInputPartFromSameNode(self, socket, useFastMethod, inputSocketNames):
		if useFastMethod:
			return inputSocketNames[socket.identifier] + " = " + getInputValueVariable(socket)
		else:
			return "'" + socket.identifier + "' : " + getInputValueVariable(socket)
	def getInputPartFromOtherNode(self, socket, originSocket, useFastMethod, inputSocketNames):
		return self.getInputPartStart(socket, useFastMethod, inputSocketNames) + getInputValueVariable(socket)	
	def getInputPartStart(self, socket, useFastMethod, inputSocketNames):
		if useFastMethod:
			return inputSocketNames[socket.identifier] + " = "
		else:
			return "'" + socket.identifier + "' : "
		
		
		
	def getNodeDeclarationString(self, node):
		return getNodeVariableName(node) + " = nodes['"+node.name+"']"
	def getNodeFunctionDeclarationString(self, node):
		return getNodeExecutionName(node) + " = " + getNodeVariableName(node) + ".execute"
	def getSocketDeclarationString(self, socket):
		return getInputSocketVariableName(socket) + " = " + getNodeVariableName(socket.node) + ".inputs['" + socket.name + "'].getValue()"
	def getNodeExecutionLines(self, node):
		useInLineExecution = False
		if hasattr(node, "useInLineExecution"):
			useInLineExecution = node.useInLineExecution()
		if useInLineExecution:
			if hasattr(node, "getModuleList"):
				self.modules.update(node.getModuleList())
			inLineString = node.getInLineExecutionString(getOutputUseDictionary(node)) 
			inputSocketNames = node.getInputSocketNames()
			outputSocketNames = node.getOutputSocketNames()
			for identifier, name in inputSocketNames.items():
				socket = node.inputs[identifier]
				inLineString = inLineString.replace("%" + name + "%", getInputValueVariable(socket))
				if not hasOtherDataOrigin(socket):
					self.neededSocketReferences.append(socket)
			for identifier, name in outputSocketNames.items():
				inLineString = inLineString.replace("$" + name + "$", getOutputValueVariable(node.outputs[identifier]))
			return inLineString.split("\n")
		else:
			self.executeNodes.append(node)
			return [getNodeOutputString(node) + " = " + getNodeExecutionName(node) + "(" + self.generateInputListString(node) + ")"]
			
def getNodeOutputString(node):
	if usesFastCall(node):
		outputSocketNames = node.getOutputSocketNames()
		if len(outputSocketNames) != len(node.outputs): raise Exception()
		if len(node.outputs) != 0:
			outputParts = []
			for socket in node.outputs:
				outputParts.append(getOutputValueVariable(socket))
			return ", ".join(outputParts)
	return getNodeOutputName(node)

def getOutputUseDictionaryCode(node):
	codeParts = []
	for socket in node.outputs:
		codeParts.append('"' + socket.identifier + '" : ' + str(isOutputSocketUsed(socket)))
	return "{" + ", ".join(codeParts) + "}"
def getOutputUseDictionary(node):
	outputUse = {}
	for socket in node.outputs:
		outputUse[socket.identifier] = isOutputSocketUsed(socket)
	return outputUse
	
def getCorrespondingStartNode(node):
	return node.getStartNode()
		
def isExecuteableNode(node):
	return hasattr(node, "execute")
def isInLineNode(node):
	return hasattr(node, "getInLineExecutionString")
def isForLoopNode(node):
	return node.bl_idname == "mn_ForLoopNode"
	
def usesFastCall(node):
	if hasattr(node, "getInputSocketNames"):
		if hasattr(node, "getOutputSocketNames"): return True
		else: raise Exception()
	if hasattr(node, "getOutputSocketNames"): raise Exception()
	return False
def usesOutputUseParameter(node):
	return hasattr(node, "outputUseParameterName")
	
def getInputValueVariable(socket):
	originSocket = getDataOriginSocket(socket)
	if originSocket is not None:
		return getOutputValueVariable(originSocket)
	else:
		return getInputSocketVariableName(socket)
def getOutputValueVariable(socket):
	if usesFastCall(socket.node):
		outputSocketNames = socket.node.getOutputSocketNames()
		return getNodeOutputName(socket.node) + "_" + outputSocketNames[socket.identifier]
	else:
		return getNodeOutputName(socket.node) + "['" + socket.identifier + "']"
		
def getNodeVariableName(node):
	return "node_" + str(node.codeIndex)
def getNodeInputName(node):
	return "input_" + str(node.codeIndex)
def getNodeOutputName(node):
	return "output_" + str(node.codeIndex)
def getNodeOutputUseName(node):
	return getNodeVariableName(node) + "_output_use"
def getNodeFunctionName(node):
	return getNodeVariableName(node) + "_" + "Function"
def getNodeExecutionName(node):
	return getNodeVariableName(node) + "_" + "execute"
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
		originSocket = getDataOriginSocket(socket)
		if originSocket is not None:
			node = originSocket.node
			directDependencies.append(node)
	return directDependencies
	
	
# cleanup of node trees
################################

convertRules = {}
convertRules[("Float", "Integer")] = "mn_ToIntegerConversion"
convertRules[("Generic", "Integer")] = "mn_ToIntegerConversion"
convertRules[("Float", "String")] = "mn_ToStringConversion"
convertRules[("Generic", "Float")] = "mn_ToFloatConversion"
convertRules[("Integer", "String")] = "mn_ToStringConversion"
convertRules[("Float", "Vector")] = "mn_CombineVector"
convertRules[("Integer", "Vector")] = "mn_CombineVector"
convertRules[("Vector", "Float")] = "mn_SeparateVector"
convertRules[("Vector", "Integer")] = "mn_SeparateVector"
		
def cleanupNodeTrees():
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:
		cleanupNodeTree(nodeTree)
def cleanupNodeTree(nodeTree):
	originalLinks = list(nodeTree.links)
	for link in originalLinks:
		toSocket = link.to_socket
		fromSocket = link.from_socket
		if toSocket.node.type == "REROUTE":
			continue
		if fromSocket.node.type == "REROUTE": originSocket = getOriginSocket(toSocket)
		else: originSocket = fromSocket
		if isOtherOriginSocket(toSocket, originSocket):
			if originSocket.dataType not in toSocket.allowedInputTypes and toSocket.allowedInputTypes[0] != "all":
				handleNotAllowedLink(nodeTree, link, fromSocket, toSocket, originSocket)
			else: setDataConnection(originSocket, toSocket)
def handleNotAllowedLink(nodeTree, link, fromSocket, toSocket, originSocket):
	fromType = originSocket.dataType
	toType = toSocket.dataType
	nodeTree.links.remove(link)
	convertNodeType = convertRules.get((fromType, toType))
	if convertNodeType is not None:
		insertConversionNode(nodeTree, convertNodeType, fromSocket, toSocket, originSocket)
def insertConversionNode(nodeTree, convertNodeType, fromSocket, toSocket, originSocket):
	node = nodeTree.nodes.new(convertNodeType)
	node.hide = True
	node.select = False
	x1, y1 = toSocket.node.location
	x2, y2 = list(fromSocket.node.location)
	node.location = [(x1+x2)/2+20, (y1+y2)/2-50]
	
	nodeTree.links.new(node.inputs[0], fromSocket)
	setDataConnection(originSocket, node.inputs[0])
	
	nodeTree.links.new(toSocket, node.outputs[0])
	setDataConnection(node.outputs[0], toSocket)
	
	
	
# find origin sockets
############################################

inputSockets = {}
outputSockets = {}
					
def handleLink(link):
	fromValid = isValidNode(link.from_node)
	toValid = isValidNode(link.to_node)
	if fromValid and toValid: setDataConnection(link.from_socket, link.to_socket)
	elif toValid:
		originSocket = getOriginSocket(link.to_socket)
		if isOtherOriginSocket(link.to_socket, originSocket):
			setDataConnection(originSocket, link.to_socket)
					
def clearSocketConnections():
	global inputSockets, outputSockets
	inputSockets = {}
	outputSockets = {}
				
def setDataConnection(fromSocket, toSocket):
	global inputSockets, outputSockets
	
	if fromSocket not in outputSockets:	outputSockets[fromSocket] = []
	
	inputSockets[toSocket] = fromSocket
	outputSockets[fromSocket].append(toSocket)
			
def isValidNode(node):
	return node.bl_idname[:3] == "mn_"

def hasOtherDataOrigin(socket):
	return inputSockets.get(socket) is not None
def getDataOriginSocket(socket):
	return inputSockets.get(socket)
def isOutputSocketUsed(socket):
	return socket in outputSockets
def getSocketsFromOutputSocket(socket):
	return outputSockets.get(socket, [])
			