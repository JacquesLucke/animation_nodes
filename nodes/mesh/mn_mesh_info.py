import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_MeshInfo(Node, AnimationNode):
	bl_idname = "mn_MeshInfo"
	bl_label = "Mesh Info"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_MeshSocket", "Mesh").showName = False
		self.outputs.new("mn_VertexListSocket", "Vertices")
		self.outputs.new("mn_PolygonListSocket", "Polygons")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Mesh" : "mesh"}
	def getOutputSocketNames(self):
		return {"Vertices" : "vertices",
				"Polygons" : "polygons"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		codeLines.append("$vertices$ = []")
		codeLines.append("$polygons$ = []")
		codeLines.append("try:")
		codeLines.append("    for vertex in %mesh%.vertices:")
		codeLines.append("        $vertices$.append([vertex.co, vertex.normal])")
		codeLines.append("    for polygon in %mesh%.polygons:")
		codeLines.append("        $polygons$.append([polygon.center, polygon.normal, polygon.area, polygon.material_index])")
		codeLines.append("except: pass")
		return "\n".join(codeLines)
		

classes = [
	mn_MeshInfo
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
