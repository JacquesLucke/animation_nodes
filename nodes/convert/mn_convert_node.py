import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_socket_info import *

class mn_ConvertNode(Node, AnimationNode):
	bl_idname = "mn_ConvertNode"
	bl_label = "Convert"
	
	convertType = bpy.props.StringProperty(default = "Integer")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_GenericSocket", "Old")
		self.buildOutputSocket()
		allowCompiling()
		
	def update(self):
		forbidCompiling()
		link = self.getFirstOutputLink()
		if link is not None:
			fromSocket = link.from_socket
			toSocket = link.to_socket
			if toSocket.node.type != "REROUTE":
				if fromSocket.dataType != toSocket.dataType:
					self.convertType = toSocket.dataType
					self.buildOutputSocket()
		allowCompiling()
		
	def getFirstOutputLink(self):
		links = self.getLinksFromOutputSocket()
		if len(links) == 1: return links[0]
		return None
		
	def getLinksFromOutputSocket(self):
		socket = self.outputs.get("New")
		if socket is not None:
			return socket.links
		return []
		
	def getConversionTypes(self):
		return types
	def buildOutputSocket(self):
		forbidCompiling()
		connections = getConnectionDictionaries(self)
		self.outputs.clear()
		self.outputs.new(getSocketNameByDataType(self.convertType), "New")
		tryToSetConnectionDictionaries(self, connections)
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Old" : "old"}
	def getOutputSocketNames(self):
		return {"New" : "new"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		t = self.convertType
		if t == "Float": return '''
try: $new$ = float(%old%)
except: $new$ = 0
'''
		elif t == "Integer": return '''
try: $new$ = int(%old%)
except: $new$ = 0
'''
		elif t == "String": return '''
try: $new$ = str(%old%)
except: $new$ = 0
'''
		elif t == "Object": return '''
if isinstance(%old%, bpy.types.Object): $new$ = %old%
else: $new$ = None
'''
		elif t == "Color":
			codeLines = []
			codeLines.append("try:")
			codeLines.append("    if hasattr(%old%, '__iter__'):")
			codeLines.append("        if len(%old%) == 4: $new$ = %old%[:4]")
			codeLines.append("        elif len(%old%) == 3: $new$ = %old%[:3] + [1]")
			codeLines.append("        elif len(%old%) == 2: $new$ = [%old%[0]] * 3 + [%old%[1]]")
			codeLines.append("        elif len(%old%) == 1: $new$ = [%old%[0] * 3] + [1]")
			codeLines.append("    else: $new$ = [float(%old%)] * 3 + [1]")
			codeLines.append("except: $new$ = [0, 0, 0, 1]")
			return "\n".join(codeLines)
		elif t == "Interpolation":
			codeLines = []
			codeLines.append("try:")
			codeLines.append("    if hasattr(%old%[0], '__call__'): $new$ = %old%")
			codeLines.append("    else: $new$ = (mn_interpolation_utils.linear, None)")
			codeLines.append("except: $new$ = (mn_interpolation_utils.linear, None)")
			return "\n".join(codeLines)
		else:
			return "$new$ = %old%"
			
	def getModuleList(self):
		t = self.convertType
		if t == "Interpolation": return ["mn_interpolation_utils"]
		return []