import bpy
import bmesh
from ... base_types.node import AnimationNode


class CreateMeshFromData(bpy.types.Node, AnimationNode):
    bl_idname = "an_CreateMeshFromData"
    bl_label = "Create Mesh"

    inputNames = { "Mesh Data" : "meshData" }
    outputNames = { "Mesh" : "mesh" }

    errorMessage = bpy.props.StringProperty(default = "")

    def create(self):
        self.inputs.new("an_MeshDataSocket", "Mesh Data")
        self.outputs.new("an_MeshSocket", "Mesh")

    def draw_buttons(self, context, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def execute(self, meshData):
        try:
            bm = getBMeshFromMeshData(meshData)
            self.errorMessage = ""
        except IndexError as e:
            bm = bmesh.new()
            self.errorMessage = "Missing vertices"
        except ValueError as e:
            bm = bmesh.new()
            self.errorMessage = "Multiple identical edges or polygons"
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
