import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... data_structures.mesh import Polygon, Vertex

class BMeshMeshDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BMeshMeshDataNode"
    bl_label = "BMesh Mesh Data"

    def create(self):
        self.newInput("BMesh", "BMesh", "bm")

        self.newOutput("Vector List", "Vertex Locations", "vertexLocations")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")
        self.newOutput("Vertex List", "Vertices", "vertices")
        self.newOutput("Polygon List", "Polygons", "polygons")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

#        yield "meshName = ''"
#        yield "if getattr(object, 'type', '') == 'MESH':"
#        yield "    mesh = self.getMesh(object, useModifiers, scene)"
#        yield "    meshName = mesh.name"

        yield "if bm:"
        if isLinked["vertexLocations"]:
            yield "    vertexLocations = self.getVertexLocations(bm)"
        if isLinked["edgeIndices"]:
            yield "    edgeIndices = self.getEdgeIndices(bm)"
        if isLinked["polygonIndices"]:
            yield "    polygonIndices = self.getPolygonIndices(bm)"
        if isLinked["vertices"]:
            yield "    vertices = self.getVertices(bm)"
        if isLinked["polygons"]:
            yield "    polygons = self.getPolygons(bm)"

#        yield "    self.clearMesh(mesh, useModifiers, scene)"
        yield "else: vertexLocations, edgeIndices, polygonIndices, vertices, polygons = [], [], [], [], []"


#    def getMesh(self, object, useModifiers, scene):
#        if useModifiers and scene is not None:
#            settings = "RENDER" if isRendering() else "PREVIEW"
#            return object.to_mesh(scene = scene, apply_modifiers = True, settings = settings)
#        return object.data

#    def clearMesh(self, mesh, useModifiers, scene):
#        if useModifiers and scene is not None: bpy.data.meshes.remove(mesh)

    def getVertexLocations(self, BMesh):
        return [v.co for v in BMesh.verts]

    def getEdgeIndices(self, BMesh):
        return [tuple(v.index for v in edge.verts) for edge in BMesh.edges]

    def getPolygonIndices(self, BMesh):
        return [tuple(v.index for v in face.verts) for face in BMesh.faces]

    def getVertices(self, BMesh):
        return [Vertex.fromBMeshVert(vert) for vert in BMesh.verts]

    def getPolygons(self, BMesh):
        return [Polygon.fromBMeshFace(face) for face in BMesh.faces]
