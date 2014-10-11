import bpy
from mn_utils import *

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
		codeParts.append(self.getNodeTreeExecutionFinishedCalls())
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
		startNode = getSubProgramStartNodeOfNetwork(functionNetwork)
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
		elif isSubProgramNode(node):
			codeLines.extend(self.getSubProgramNodeCode(node))
		elif isEnumerateObjectsNode(node):
			codeLines.extend(self.getEnumerateObjectsNodeCode(node))
		return codeLines		
		
	def getExecutableNodeCode(self, node):
		codeLines = []
		if bpy.context.scene.nodeExecutionProfiling: codeLines.append(getNodeTimerStartName(node) + " = time.clock()")
		codeLines.append(self.getNodeExecutionString(node))
		if bpy.context.scene.nodeExecutionProfiling: codeLines.append(getNodeTimerName(node) + " += time.clock() - " + getNodeTimerStartName(node))
		return codeLines
	def getSubProgramNodeCode(self, node):
		codeLines = []
		codeLines.append(getNodeInputName(node) + " = " + self.generateInputListString(node))
		startNode = getCorrespondingStartNode(node)
		if startNode is not None:
			codeLines.append("for i in range(" + getNodeInputName(node) + "['Amount']):")
			codeLines.append("    " + getNodeInputName(node) + "['Index'] = i")
			codeLines.append("    " + getNodeFunctionName(startNode) + "(" + getNodeInputName(node) + ")")
			self.makeFunctionCode(subPrograms[getNodeIdentifier(startNode)])
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
			self.makeFunctionCode(subPrograms[getNodeIdentifier(startNode)])
		codeLines.append(getNodeOutputName(node) + " = " + inputName)
		return codeLines

	def getNodeTreeExecutionFinishedCalls(self):
		codeLines = []
		for node in self.allNodesInTree:
			if hasattr(node, "executionFinished"):
				codeLines.append(getNodeVariableName(node) + ".executionFinished()")
		return "\n" + "\n".join(codeLines) + "\n"
		
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
		useFastMethod = hasattr(node, "getSocketVariableConnections")
		socketVarNames = None
		if useFastMethod: socketVarNames = node.getSocketVariableConnections()[0]
		for socket in node.inputs:
			originSocket = getOriginSocket(socket)
			if isOtherOriginSocket(socket, originSocket):
				inputParts.append(self.getInputPartFromOtherNode(socket, originSocket, useFastMethod, socketVarNames))
			else:
				self.neededSocketReferences.append(socket)
				inputParts.append(self.getInputPartFromSameNode(socket, useFastMethod, socketVarNames))
		
		return self.joinInputParts(inputParts, useFastMethod)
			
	def joinInputParts(self, inputParts, useFastMethod):
		if useFastMethod:
			return ", ".join(inputParts)
		else:
			return "{ " + ", ".join(inputParts) + " }"
	def getInputPartFromSameNode(self, socket, useFastMethod, socketVarNames):
		if useFastMethod:
			return socketVarNames[socket.identifier] + " = " + getInputSocketVariableName(socket)
		else:
			return "'" + socket.identifier + "' : " + getInputSocketVariableName(socket)
	def getInputPartFromOtherNode(self, socket, originSocket, useFastMethod, socketVarNames):
		originNode = originSocket.node
		originUsesFastMethod = hasattr(originNode, "getSocketVariableConnections")
		
		originSocketVarNames = None
		if originUsesFastMethod: 
			originSocketVarNames = originNode.getSocketVariableConnections()[1]
			
		return self.getInputPartStart(socket, useFastMethod, socketVarNames) + self.getInputPartEnd(originNode, originSocket, originUsesFastMethod, originSocketVarNames)
	
	def getInputPartStart(self, socket, useFastMethod, socketVarNames):
		if useFastMethod:
			return socketVarNames[socket.identifier] + " = "
		else:
			return "'" + socket.identifier + "' : "
	
	def getInputPartEnd(self, originNode, originSocket, originUsesFastMethod, originSocketVarNames):
		if originUsesFastMethod:
			return getNodeOutputName(originNode) + "_" + originSocketVarNames[originSocket.identifier]
		else:
			return getNodeOutputName(originNode) + "['" + originSocket.identifier + "']"
		
		
		
	def getNodeDeclarationString(self, node):
		return getNodeVariableName(node) + " = nodes['"+node.name+"']"
	def getSocketDeclarationString(self, socket):
		return getInputSocketVariableName(socket) + " = " + getNodeVariableName(socket.node) + ".inputs['" + socket.identifier + "'].getValue()"
	def getNodeExecutionString(self, node):
		return getNodeOutputString(node) + " = " + getNodeVariableName(node) + ".execute(" + self.generateInputListString(node) + ")"

def getNodeOutputString(node):
	if hasattr(node, "getSocketVariableConnections"):
		con = node.getSocketVariableConnections()[1]
		outputParts = []
		for socket in node.outputs:
			outputParts.append(getNodeOutputName(node) + "_" + con[socket.identifier])
		return ", ".join(outputParts)
	else:
		return getNodeOutputName(node)
	
def getCorrespondingStartNode(node):
	return node.getStartNode()
		
def isExecuteableNode(node):
	return hasattr(node, "execute")
def isSubProgramNode(node):
	return node.bl_idname == "SubProgramNode"
def isEnumerateObjectsNode(node):
	return node.bl_idname == "EnumerateObjectsNode"
		
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