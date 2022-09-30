import bpy
import bmesh
from bpy.props import *
from ... base_types import AnimationNode

class CreateBMeshFromMesh(AnimationNode, bpy.types.Node):
    bl_idname = "an_CreateBMeshFromMeshNode"
    bl_label = "Create BMesh"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Mesh", "Mesh", "meshData")
        self.newOutput("BMesh", "BMesh", "bm")

    def execute(self, meshData):
        try:
            return getBMeshFromMesh(meshData)
        except IndexError as e:
            self.raiseErrorMessage("Missing vertices")
        except ValueError as e:
            self.raiseErrorMessage("Multiple identical edges or polygons")


def getBMeshFromMesh(meshData):
    bm = bmesh.new()
    for co in meshData.vertices:
        bm.verts.new(co)

    # for Blender Version >= 2.73
    try: bm.verts.ensure_lookup_table()
    except: pass

    for edgeIndices in meshData.edges:
        bm.edges.new((bm.verts[edgeIndices[0]], bm.verts[edgeIndices[1]]))

    materialIndices = meshData.getBuiltInAttribute("Material Indices")
    if materialIndices is not None:
        materialIndicesData = materialIndices.data
        for polygonIndices, materialIndex in zip(meshData.polygons, materialIndicesData):
            face = bm.faces.new(tuple(bm.verts[index] for index in polygonIndices))
            face.material_index = materialIndex
    else:
        for polygonIndices in meshData.polygons:
            face = bm.faces.new(tuple(bm.verts[index] for index in polygonIndices))

    bm.normal_update()
    return bm
