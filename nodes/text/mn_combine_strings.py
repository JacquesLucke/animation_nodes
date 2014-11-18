import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.utils.mn_node_utils import *


class mn_CombineStringsNode(Node, AnimationNode):
	bl_idname = "mn_CombineStringsNode"
	bl_label = "Combine Texts"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_StringSocket", "1.")
		self.inputs.new("mn_StringSocket", "2.")
		self.inputs.new("mn_EmptySocket", "...").passiveSocketType = "mn_StringSocket"
		self.outputs.new("mn_StringSocket", "Text")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		row = layout.row(align = True)
	
		newSocket = row.operator("mn.add_combine_strings_socket", text = "New", icon = "PLUS")
		newSocket.nodeTreeName = self.id_data.name
		newSocket.nodeName = self.name
		
		removeSocket = row.operator("mn.remove_combine_strings_socket", text = "Remove", icon = "X")
		removeSocket.nodeTreeName = self.id_data.name
		removeSocket.nodeName = self.name
		
	def update(self):
		forbidCompiling()
		
		socket = self.inputs.get("...")
		updateDependencyNode(socket)
		
		if socket is not None:
			links = socket.links
			if len(links) == 1:
				link = links[0]
				fromSocket = link.from_socket
				originSocket = getOriginSocket(socket)
				self.id_data.links.remove(link)
				if originSocket is not None:
					if originSocket.dataType == "String":
						self.inputs.remove(socket)
						newSocketName = str(len(self.inputs) + 1) + "."
						newSocket = self.inputs.new("mn_StringSocket", newSocketName)
						self.inputs.new("mn_EmptySocket", "...").passiveSocketType = "mn_StringSocket"
						self.id_data.links.new(newSocket, fromSocket)
				
		allowCompiling()
		
	def execute(self, input):
		output = {}
		text = ""
		for i in range(len(self.inputs) - 1):
			identifier = str(i+1) + "."
			text += input[identifier]
		output["Text"] = text
		return output
		
	def newInputSocket(self):
		forbidCompiling()
		newSocketName = str(len(self.inputs)) + "."
		newSocket = self.inputs.new("mn_StringSocket", newSocketName)
		self.inputs.move(len(self.inputs) - 1, len(self.inputs) - 2)
		allowCompiling()
		nodeTreeChanged()
		
	def removeInputSocket(self):
		forbidCompiling()
		if len(self.inputs) > 2:
			self.inputs.remove(self.inputs[len(self.inputs) - 2])
		allowCompiling()
		nodeTreeChanged()
		
		
		
class AddCombineStringsSocket(bpy.types.Operator):
	bl_idname = "mn.add_combine_strings_socket"
	bl_label = "Add Multi Math Socket"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.newInputSocket()
		return {'FINISHED'}
		
class RemoveCombineStringsSocket(bpy.types.Operator):
	bl_idname = "mn.remove_combine_strings_socket"
	bl_label = "Remove Multi Math Socket"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.removeInputSocket()
		return {'FINISHED'}


classes = [
	mn_CombineStringsNode,
	AddCombineStringsSocket,
	RemoveCombineStringsSocket
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
