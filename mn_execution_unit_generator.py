import bpy, time
from animation_nodes.utils.mn_node_utils import *
from animation_nodes.mn_utils import *

normalNetworks = []
loopNetworks = {}
groupNetworks = {}
invalidNetworks = []
treeInfo = None
useProfiling = False

class ExecutionUnit:

	def __init__(self, code, updateSettingsNode = None):
		self.executionCode = code
		self.codeObject = compile(code, "<string>", "exec")
		self.executeAmount = 0
		self.totalExecuteTime = 0.0
		if getattr(updateSettingsNode, "bl_idname", "") == "mn_NetworkUpdateSettingsNode":
			self.updateSettingsNode = (updateSettingsNode.id_data.name, updateSettingsNode.name)
		else: self.updateSettingsNode = None
		
	def execute(self, event = "NONE"):
		update = bpy.context.scene.mn_settings.update
		developer = bpy.context.scene.mn_settings.developer
		
		onFrameChange = update.frameChange
		onSceneUpdate = update.sceneUpdate
		onPropertyChange = update.propertyChange
		onTreeChange = update.treeChange
		skipFrames = update.skipFramesAmount
		forceExecution = False
		printTime = False
		unitName = "Unit"
		
		node = None
		if self.updateSettingsNode is not None:
			node = getNode(self.updateSettingsNode[0], self.updateSettingsNode[1])
			
			onFrameChange = node.settings.frameChanged
			onSceneUpdate = node.settings.sceneUpdates
			onPropertyChange = node.settings.propertyChanged
			onTreeChange = node.settings.treeChanged
			skipFrames = node.settings.skipFramesAmount
			forceExecution = node.settings.forceExecution
			printTime = node.settings.printTime
			unitName = node.settings.unitName
			
		# don't use scene/property update when animation plays back
		if event in ["SCENE", "PROPERTY", "FRAME"]:
			if isAnimationPlaying() and onFrameChange and (onSceneUpdate or onPropertyChange):
				onSceneUpdate = False
				onPropertyChange = False
				
			# use skip frames
			if isAnimationPlaying() and getCurrentFrame() % (max(skipFrames, 0) + 1) != 0:
				onFrameChange = False
			
		# reset counter on force execution
		if forceExecution:
			self.totalExecuteTime = 0.0
			self.executeAmount = 0
			
		execute = event == "NONE" \
			or event == "FRAME" and onFrameChange \
			or event == "SCENE" and onSceneUpdate \
			or event == "PROPERTY" and onPropertyChange \
			or event == "TREE" and onTreeChange \
			or forceExecution
			
		if execute:
			start = time.clock()
			exec(self.codeObject, {})
			timeSpan = time.clock() - start
			self.totalExecuteTime += timeSpan
			self.executeAmount += 1
			if printTime:
				printTimeSpan(unitName + " exec. ", self.totalExecuteTime / self.executeAmount, "counter: " + str(self.executeAmount))
			if node is not None:
				node.executionTime = timeSpan

def getExecutionUnits():
	global useProfiling, idCounter, treeInfo
	useProfiling = bpy.context.scene.mn_settings.developer.executionProfiling
	idCounter = 0
	cleanupNodeTrees()
	treeInfo = NodeTreeInfo(getAnimationNodeTrees())
	networks = getNodeNetworks()
	prepareNetworks(networks)
	executionUnits = []
	for network in normalNetworks:
		codeGenerator = NetworkCodeGenerator(network)
		codeGenerator.generateCode()
		executionUnit = ExecutionUnit(codeGenerator.generatedCode, codeGenerator.updateSettingsNode)
		executionUnits.append(executionUnit)
	return executionUnits
	
def prepareNetworks(networks):
	global normalNetworks, loopNetworks, groupNetworks, invalidNetworks
	normalNetworks = []
	loopNetworks = {}
	groupNetworks = {}
	invalidNetworks = []
	for network in networks:
		setUniqueCodeIndexToEveryNode(network.nodes)
		if network.type == "Normal":
			normalNetworks.append(network)
		elif network.type == "Loop":
			loopNetworks[network.getLoopStartNode()] = network
		elif network.type == "Group":
			groupNetworks[network.getGroupInputNode()] = network
		elif network.type == "Invalid":
			invalidNetworks.append(network)
		
			
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
	networks = []
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:
		nodeTree.use_fake_user = True
		nodeTreeInfo = NodeTreeInfo(nodeTree)
		networks.extend(nodeTreeInfo.getNetworks())
	return networks

	
	
# network code generator class
########################################

class NetworkCodeGenerator:
	def __init__(self, network):
		self.network = network
		self.modules = set(["bpy", "time"])
		self.functions = {}
		self.neededSocketReferences = []
		self.nodeTreeNames = {}
		self.allNodesInTree = []
		self.executeNodes = []
		self.outputUseNodes = []
		self.determinedNodesCode = []
		
		self.updateSettingsNode = None
		self.generatedCode = ""
		
	def generateCode(self):
		mainCode = self.getMainCode()
		
		codeParts = []
		codeParts.append("import " + ", ".join(self.modules))
		codeParts.append(self.getNodeTreeReferencingCode())
		codeParts.append(self.getNodeReferencingCode())
		codeParts.append(self.getNodeExecuteReferencingCode())
		codeParts.append(self.getSocketReferencingCode())
		codeParts.append(self.getOutputUseDeclarationCode())
		codeParts.append(self.getTimerDefinitions())
		codeParts.append(self.getDeterminedNodesCode())
		codeParts.append(self.getFunctionsCode())
		codeParts.append(mainCode)
		codeParts.append(self.getCodeToPrintProfilingResult())
		
		self.generatedCode = "\n".join(codeParts)
		
	def getMainCode(self):
		self.allNodesInTree.extend(self.network.nodes)
		self.orderedNodes = orderNodes(self.network.nodes)
		codeLines = []
		for node in self.orderedNodes:
			if self.updateSettingsNode is None:
				self.updateSettingsNode = treeInfo.getUpdateSettingsNode(node)
			codeLines.extend(self.getNodeCodeLines(node))
		return "\n".join(codeLines)
		
	def makeLoopCode(self, loopNetwork):
		startNode = loopNetwork.getLoopStartNode()
		if startNode not in self.functions:
			self.functions[startNode] = self.getLoopCode(loopNetwork, startNode)
	def getLoopCode(self, loopNetwork, startNode):
		self.allNodesInTree.extend(loopNetwork.nodes)
		self.orderedNodes = orderNodes(loopNetwork.nodes)
		mainLines = []
		mainLines.append("def " + getNodeFunctionName(startNode) + "(" + getNodeOutputName(startNode) + "):")
		mainLines.append("    " + self.getTimerGlobalList(loopNetwork))
		for node in self.orderedNodes:
			if node != startNode:
				codeLines = self.getNodeCodeLines(node)
				self.setIndentationOnEveryLine(codeLines)
				mainLines.extend(codeLines)
		if useProfiling: mainLines.append("    globals().update(locals())")
		mainLines.append("    pass")
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
		elif isLoopCallerNode(node):
			codeLines.extend(self.getLoopNodeCode(node))
		return codeLines        
		
	def getExecutableNodeCode(self, node):
		codeLines = []
		lines = self.getNodeExecutionLines(node)
		if isDeterminedNode(node):
			self.determinedNodesCode.extend(lines)
		else:
			if useProfiling: codeLines.append(getNodeTimerStartName(node) + " = time.clock()")
			codeLines.extend(lines)
			if useProfiling: codeLines.append(getNodeTimerName(node) + " += time.clock() - " + getNodeTimerStartName(node))
		return codeLines
	def getLoopNodeCode(self, node):
		codeLines = []
		codeLines.append(getNodeInputName(node) + " = " + self.generateInputListString(node))
		startNode = node.getStartNode()
		if startNode is not None:
			fromListSockets = startNode.getSocketDescriptions()[0]
			
			if len(fromListSockets) == 0:
				codeLines.append(getNodeInputName(node) + "['List Length'] = " + getNodeInputName(node) + "['Amount']")
				codeLines.append("for " + getNodeInputName(node) + "['Index'] in range(" + getNodeInputName(node) + "['Amount']):")
			else:
				codeLines.append("try: " + self.getZipListCode(node, fromListSockets))
				codeLines.append("except: zippedList = []")
				codeLines.append(getNodeInputName(node) + "['List Length'] = len(zippedList)")
				codeLines.append(self.getEnumerateLoopHeader(node, fromListSockets))
			
			codeLines.append("    " + getNodeFunctionName(startNode) + "(" + getNodeInputName(node) + ")")
			self.makeLoopCode(loopNetworks[startNode])
		codeLines.append(getNodeOutputName(node) + " = " + getNodeInputName(node))
		return codeLines
		
	# zippedList = list(zip(list1, list2, list3))
	def getZipListCode(self, node, fromListSockets):
		codeParts = []
		codeParts.append("zippedList = list(zip(")
		
		listVariables = []
		for socket in fromListSockets:
			listVariables.append(getNodeInputName(node) + "['" + socket.identifier + "list']")
			
		codeParts.append(", ".join(listVariables))
		codeParts.append("))")
		
		return "".join(codeParts)
	# for (input['Index'], (element1, element2, element3,)) in enumerate(zippedList):
	def getEnumerateLoopHeader(self, node, fromListSockets):
		codeParts = []
		codeParts.append("for (" + getNodeInputName(node) + "['Index']" + ", (")
		
		listVariables = []
		for socket in fromListSockets:
			listVariables.append(getNodeInputName(node) + "['" + socket.identifier + "']")
			
		codeParts.append(", ".join(listVariables))
		codeParts.append(",)) in enumerate(zippedList):")
		
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
			for node in network.nodes:
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
		
	def getDeterminedNodesCode(self):
		return "\n".join(self.determinedNodesCode)
		
	def getNodeTreeReferencingCode(self):
		nodeTrees = []
		for node in self.allNodesInTree:
			if node.id_data not in nodeTrees: nodeTrees.append(node.id_data)
		codeLines = []
		for i, nodeTree in enumerate(nodeTrees):
			nodeTreeVarName = "nodes" + str(i)
			self.nodeTreeNames[nodeTree] = nodeTreeVarName
			codeLines.append(nodeTreeVarName + " = bpy.data.node_groups['" + nodeTree.name + "'].nodes")
		return "\n".join(codeLines)
		
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
			originSocket = treeInfo.getDataOriginSocket(socket)
			if originSocket is not None:
				inputParts.append(self.getInputPartFromOtherNode(socket, originSocket, useFastMethod, inputSocketNames))
			else:
				self.neededSocketReferences.append(socket)
				inputParts.append(self.getInputPartFromSameNode(socket, useFastMethod, inputSocketNames))
		if usesOutputUseParameter(node):
			self.outputUseNodes.append(node)
			joinedInputParts = self.joinInputParts(inputParts, useFastMethod)
			if len(joinedInputParts) > 0:
				return node.outputUseParameterName + " = " + getNodeOutputUseName(node) + ", " + self.joinInputParts(inputParts, useFastMethod)
			else:
				return node.outputUseParameterName + " = " + getNodeOutputUseName(node)
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
		return getNodeVariableName(node) + " = " + self.nodeTreeNames[node.id_data] + "['"+node.name+"']"
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
				if not treeInfo.hasOtherDataOrigin(socket):
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
		codeParts.append('"' + socket.identifier + '" : ' + str(treeInfo.isOutputSocketUsed(socket)))
	return "{" + ", ".join(codeParts) + "}"
def getOutputUseDictionary(node):
	outputUse = {}
	for socket in node.outputs:
		outputUse[socket.identifier] = treeInfo.isOutputSocketUsed(socket)
	return outputUse
	
		
def isExecuteableNode(node):
	return hasattr(node, "execute")
def isInLineNode(node):
	return hasattr(node, "getInLineExecutionString")
def isLoopCallerNode(node):
	return node.bl_idname == "mn_LoopCallerNode"
	
def usesFastCall(node):
	if hasattr(node, "getInputSocketNames"):
		if hasattr(node, "getOutputSocketNames"): return True
		else: raise Exception()
	if hasattr(node, "getOutputSocketNames"): raise Exception()
	return False
def usesOutputUseParameter(node):
	return hasattr(node, "outputUseParameterName")
	
def getInputValueVariable(socket):
	originSocket = treeInfo.getDataOriginSocket(socket)
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
		
def isDeterminedNode(node):
	if getattr(node, "isDetermined", False):
		for socket in node.inputs:
			originNode = treeInfo.getDataOriginNode(socket)
			if originNode is not None:
				if not isDeterminedNode(originNode): return False
		return True
	return False
		
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
		originSocket = treeInfo.getDataOriginSocket(socket)
		if originSocket is not None:
			node = originSocket.node
			directDependencies.append(node)
	return directDependencies
	
	
# cleanup of node trees
################################

convertRules = {}
convertRules[("Float", "Integer")] = "mn_ConvertNode"
convertRules[("Generic", "Integer")] = "mn_ConvertNode"
convertRules[("Float", "String")] = "mn_ConvertNode"
convertRules[("Generic", "Float")] = "mn_ConvertNode"
convertRules[("Integer", "String")] = "mn_ConvertNode"
convertRules[("Float", "Vector")] = "mn_CombineVector"
convertRules[("Integer", "Vector")] = "mn_CombineVector"
convertRules[("Vector", "Float")] = "mn_SeparateVector"
convertRules[("Text Block", "String")] = "mn_TextBlockReader"

for dataType in ["Object", "Vertex", "Polygon", "Float", "Vector", "String"]:
	convertRules[(dataType + " List", "Integer")] = "mn_GetListLengthNode"
		
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
def handleNotAllowedLink(nodeTree, link, fromSocket, toSocket, originSocket):
	fromType = originSocket.dataType
	toType = toSocket.dataType
	nodeTree.links.remove(link)
	if fromType == "Generic":
		convertNodeType = "mn_ConvertNode"
	else:convertNodeType = convertRules.get((fromType, toType))
	if convertNodeType is not None:
		insertConversionNode(nodeTree, convertNodeType, fromSocket, toSocket, originSocket)
def insertConversionNode(nodeTree, convertNodeType, fromSocket, toSocket, originSocket):
	node = nodeTree.nodes.new(convertNodeType)
	node.hide = True
	node.select = False
	
	if convertNodeType == "mn_ConvertNode":
		node.convertType = toSocket.dataType
		node.buildOutputSocket()
	
	x1, y1 = toSocket.node.location
	x2, y2 = list(fromSocket.node.location)
	node.location = [(x1+x2)/2+20, (y1+y2)/2-50]
	
	nodeTree.links.new(node.inputs[0], fromSocket)
	nodeTree.links.new(toSocket, node.outputs[0])
		
