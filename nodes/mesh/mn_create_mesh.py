import bpy, bmesh
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
import bmesh

class mn_CreateMeshFromData(Node, AnimationNode):
	bl_idname = "mn_CreateMeshFromData"
	bl_label = "Create Mesh"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_PolygonListSocket", "Polygons")
		self.outputs.new("mn_MeshSocket", "Mesh")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def getInputSocketNames(self):
		return {"Polygons" : "polygons"}
	def getOutputSocketNames(self):
		return {"Mesh" : "mesh"}
		
	def execute(self, polygons):
		return getBMeshFromPolygons(polygons)