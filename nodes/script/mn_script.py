import bpy
from animation_nodes.mn_utils import *
from bpy.types import Node
from animation_nodes.sockets.mn_socket_info import *
from animation_nodes.utils.mn_node_utils import *
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

textBlockData = {}

class mn_ScriptNode(Node, AnimationNode):
	bl_idname = "mn_ScriptNode"
	bl_label = "Script"
	
	def selectedScriptChanged(self, context):
		updateScripts()
		self.buildSockets()
		self.errorMessage = ""
		nodeTreeChanged()
		
	def getScriptNameItems(self, context):
		scriptNames = self.getScriptNamesInTextBlock()
		scriptNameItems = []
		for scriptName in scriptNames:
			scriptNameItems.append((scriptName, scriptName, ""))
		if len(scriptNameItems) == 0: scriptNameItems.append(("NONE", "NONE", ""))
		return scriptNameItems
		
	textBlockName = bpy.props.StringProperty(default = "", update = selectedScriptChanged)
	scriptName = bpy.props.EnumProperty(items = getScriptNameItems, update = selectedScriptChanged, name = "Script Name")
	errorMessage = bpy.props.StringProperty(default = "")
	
	def init(self, context):
		forbidCompiling()
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.operator("mn.update_scripts", text = "Update Scripts", icon = "FILE_REFRESH")
	
		layout.prop_search(self, "textBlockName",  bpy.data, "texts", icon="NONE", text = "Code")
		if self.scriptName != "NONE":
			layout.prop(self, "scriptName", text = "Script")
			
		if self.errorMessage != "":
			layout.label(self.errorMessage, icon = "ERROR")
	
	def buildSockets(self):
		global textBlockData
		connections = getConnectionDictionaries(self)
		self.removeSockets()
		if self.textBlockName == "":
			return
		vars = textBlockData[self.textBlockName][1]
		
		socketDescriptionName = getSocketDefinitionName(self.scriptName)
		if socketDescriptionName in vars:
			socketDescription = vars.get(socketDescriptionName)
			self.buildSocketsFromDescription(socketDescription)
			
		tryToSetConnectionDictionaries(self, connections)
			
	def buildSocketsFromDescription(self, socketDescription):
		forbidCompiling()
		try:
			inputDescription = socketDescription[0]
			for d in inputDescription:
				blName = getSocketNameByDataType(d[0])
				name = d[1]
				identifier = d[2]
				self.inputs.new(blName, name, identifier)
				
			outputDescription = socketDescription[1]
			for d in outputDescription:
				blName = getSocketNameByDataType(d[0])
				name = d[1]
				self.outputs.new(blName, name)
			self.errorMessage = ""
		except:
			self.errorMessage = "cannot build sockets"
			self.removeSockets()
		allowCompiling()
		nodeTreeChanged()
		
	def removeSockets(self):
		self.inputs.clear()
		self.outputs.clear()

	def execute(self, input):
		output = {}
		
		if self.scriptName in ["NONE", ""]:
			return output
		
		if self.textBlockName not in textBlockData:
			updateScripts()
		try:
			if self.errorMessage == "cannot build sockets": raise
			
			functionOutput = textBlockData[self.textBlockName][1][getExecuteFunctionName(self.scriptName)](**input)
			
			if len(self.outputs) == 1:
				output[self.outputs[0].identifier] = functionOutput
			else:
				for i, socket in enumerate(self.outputs):
					output[socket.identifier] = functionOutput[i]
					
			self.errorMessage = ""
		except BaseException as e:
			self.errorMessage = str(e)
			for socket in self.outputs:
				output[socket.identifier] = socket.getValue()
		
		return output
		
		
	def getScriptNamesInTextBlock(self):
		global textBlockData
		if self.textBlockName == "":
			return []
			
		if self.textBlockName not in textBlockData:
			updateScripts()
		names = textBlockData[self.textBlockName][0].co_names
		
		scriptNames = set()
		for name in names:
			if isApiName(name):
				scriptNames.update([getScriptName(name)])
				
		validScriptNames = []
		for name in scriptNames:
			if isValidScriptName(name, names):
				validScriptNames.append(name)
		return validScriptNames
				
			
def isApiName(name):
	return ("__sockets__" in name or
			"__execute__" in name)
			
def isValidScriptName(scriptName, names):
	return hasSocketDefinition(scriptName, names) and hasExecuteFunction(scriptName, names)
def hasSocketDefinition(scriptName, names):
	return getSocketDefinitionName(scriptName) in names
def hasExecuteFunction(scriptName, names):
	return getExecuteFunctionName(scriptName) in names
	
def getSocketDefinitionName(scriptName):
	return scriptName + "__sockets__"
def getExecuteFunctionName(scriptName):
	return scriptName + "__execute__"
			
def getScriptName(varName):
	return varName[:varName.find("__")]
			
def updateScripts():
	global textBlockData
	textBlockData.clear()
	textBlocks = getUsedTextBlocks()
	for textBlock in textBlocks:
		compiledTextBlock = compileTextBlock(textBlock)
		vars = {}
		exec(compiledTextBlock, vars)
		textBlockData[textBlock.name] = (compiledTextBlock, vars)
		
	for scriptNode in getNodesFromType("mn_ScriptNode"):
		scriptNode.buildSockets()
	
			
def getUsedTextBlocks():
	textBlockNames = getUsedTextBlockNames()
	textBlocks = []
	for textBlockName in textBlockNames:
		textBlock = bpy.data.texts.get(textBlockName)
		if textBlock is not None:
			textBlocks.append(textBlock)
	return textBlocks
	
def getUsedTextBlockNames():
	scriptNodes = getNodesFromType("mn_ScriptNode")
	textBlockNames = set()
	for scriptNode in scriptNodes:
		if scriptNode.textBlockName != "":
			textBlockNames.update([scriptNode.textBlockName])
	return textBlockNames
	
def compileTextBlock(textBlock):
	return compile(textBlock.as_string(), "<string>", "exec")
			
class UpdateScripts(bpy.types.Operator):
	bl_idname = "mn.update_scripts"
	bl_label = "Update Scripts"

	def execute(self, context):
		updateScripts()
		return {'FINISHED'}
		


