import bpy, time
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *
from animation_nodes.mn_cache import *

cacheIdentifier = "Object Mesh Data"

class mn_ObjectMeshInfo(Node, AnimationNode):
	bl_idname = "mn_ObjectMeshInfo"
	bl_label = "Object Mesh Info"
	outputUseParameterName = "useOutput"
	
	usePerObjectCache = bpy.props.BoolProperty(name = "Use Cache", default = False, description = "Warning: Modifications to the data will overwrite the cache.")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.outputs.new("mn_PolygonListSocket", "Polygons")
		self.outputs.new("mn_VertexListSocket", "Vertices")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "usePerObjectCache")
		
	def getInputSocketNames(self):
		return {"Object" : "object"}
	def getOutputSocketNames(self):
		return {"Polygons" : "polygons",
				"Vertices" : "vertices"}
		
	def execute(self, object, useOutput):
		if object is None: return [], []
		if object.type != "MESH": return [], []
		
		cache = self.getInitializedCache()
		
		polygons = cacheFunctionResult(cache, object.name + "POLYGONS", getPolygonsFromMesh, [object.data], self.usePerObjectCache)
		vertices = cacheFunctionResult(cache, object.name + "VERTICES", getVerticesFromMesh, [object.data], self.usePerObjectCache)
		
		return polygons, vertices
		
	def getInitializedCache(self):
		cache = getLongTimeCache(cacheIdentifier)
		if cache is None:
			cache = {}
			setLongTimeCache(cacheIdentifier, cache)
		return cache
