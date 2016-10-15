import bpy
from bpy.props import *
from . operators.callbacks import executeCallback
from . data_structures import (Vector3DList, EdgeIndicesList, PolygonIndicesList,
                               FloatList, DoubleList)

def register():
    bpy.types.Context.getActiveAnimationNodeTree = getActiveAnimationNodeTree
    bpy.types.Operator.an_executeCallback = _executeCallback
    bpy.types.Mesh.an = PointerProperty(type = MeshProperties)

def unregister():
    del bpy.types.Context.getActiveAnimationNodeTree
    del bpy.types.Operator.an_executeCallback
    del bpy.types.Mesh.an

def getActiveAnimationNodeTree(context):
    if context.area.type == "NODE_EDITOR":
        tree = context.space_data.node_tree
        if getattr(tree, "bl_idname", "") == "an_AnimationNodeTree":
            return tree

def _executeCallback(operator, callback, *args, **kwargs):
    executeCallback(callback, *args, **kwargs)

class MeshProperties(bpy.types.PropertyGroup):
    bl_idname = "an_MeshProperties"

    def getVertices(self):
        vertices = Vector3DList(length = len(self.mesh.vertices))
        self.mesh.vertices.foreach_get("co", vertices.getMemoryView())
        return vertices

    def getEdgeIndices(self):
        edges = EdgeIndicesList(length = len(self.mesh.edges))
        self.mesh.edges.foreach_get("vertices", edges.getMemoryView())
        return edges

    def getPolygonIndices(self):
        polygons = PolygonIndicesList(
                        indicesAmount = len(self.mesh.loops),
                        polygonAmount = len(self.mesh.polygons))
        self.mesh.polygons.foreach_get("vertices", polygons.indices.getMemoryView())
        self.mesh.polygons.foreach_get("loop_total", polygons.polyLengths.getMemoryView())
        self.mesh.polygons.foreach_get("loop_start", polygons.polyStarts.getMemoryView())
        return polygons

    def getVertexNormals(self):
        normals = Vector3DList(length = len(self.mesh.vertices))
        self.mesh.vertices.foreach_get("normal", normals.getMemoryView())
        return normals

    def getPolygonNormals(self):
        normals = Vector3DList(length = len(self.mesh.polygons))
        self.mesh.polygons.foreach_get("normal", normals.getMemoryView())
        return normals

    def getPolygonCenters(self):
        centers = Vector3DList(length = len(self.mesh.polygons))
        self.mesh.polygons.foreach_get("center", centers.getMemoryView())
        return centers

    def getPolygonAreas(self):
        areas = FloatList(length = len(self.mesh.polygons))
        self.mesh.polygons.foreach_get("area", areas.getMemoryView())
        return DoubleList.fromValues(areas)

    @property
    def mesh(self):
        return self.id_data
