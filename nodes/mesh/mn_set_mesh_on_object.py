import bpy, bmesh
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
import bmesh

class mn_SetMeshOnObject(Node, AnimationNode):
	bl_idname = "mn_SetMeshOnObject"
	bl_label = "Set Mesh"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_MeshSocket", "Mesh")
		self.outputs.new("mn_ObjectSocket", "Object")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def getInputSocketNames(self):
		return {"Object" : "object",
				"Mesh" : "bmesh"}
	def getOutputSocketNames(self):
		return {"Object" : "object"}
		
	def execute(self, object, bmesh):
		if object is None: return object
		if object.type == "MESH":
			bmesh.to_mesh(object.data)
		return object