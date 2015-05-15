import bpy, bmesh
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from ... utils.mn_mesh_utils import *
import bmesh

class mn_CreateMeshFromData(Node, AnimationNode):
    bl_idname = "mn_CreateMeshFromData"
    bl_label = "Create Mesh"
    
    errorMessage = bpy.props.StringProperty(default = "")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_MeshDataSocket", "Mesh Data")
        self.outputs.new("mn_MeshSocket", "Mesh")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")
        
    def getInputSocketNames(self):
        return {"Mesh Data" : "meshData"}
    def getOutputSocketNames(self):
        return {"Mesh" : "mesh"}
        
    def execute(self, meshData):
        try:
            bm = getBMeshFromMeshData(meshData)
            self.errorMessage = ""
        except IndexError as e:
            bm = bmesh.new()
            self.errorMessage = "Missing vertices"
        return bm
            
def getBMeshFromMeshData(meshData):
    bm = bmesh.new()
    for co in meshData.vertices:
        bm.verts.new(co)
        
    # for Blender Version >= 2.73
    try: bm.verts.ensure_lookup_table()
    except: pass
    
    for edgeIndices in meshData.edges:
        bm.edges.new((bm.verts[edgeIndices[0]], bm.verts[edgeIndices[1]]))
    for polygonIndices in meshData.polygons:
        bm.faces.new(tuple(bm.verts[index] for index in polygonIndices))
    return bm