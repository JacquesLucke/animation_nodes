import bpy, bmesh
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_MeshRecalculateFaceNormals(Node, AnimationNode):
	bl_idname = "mn_MeshRecalculateFaceNormals"
	bl_label = "Calculate Face Normals"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_MeshSocket", "Mesh")
		self.outputs.new("mn_MeshSocket", "Mesh")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Mesh" : "bm"}
	def getOutputSocketNames(self):
		return {"Mesh" : "mesh"}
		
	def execute(self, bm):
		bmesh.ops.recalc_face_normals(bm, faces = bm.faces)
		return bm