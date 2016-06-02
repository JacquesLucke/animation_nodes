import bpy
from bpy.props import *
from ... events import isRendering
from ... utils.math import extractRotation
from ... base_types.node import AnimationNode
from ... data_structures.mesh import Polygon, Vertex

class ObjectMeshDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectMeshDataNode"
    bl_label = "Object Mesh Data"

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Boolean", "Use World Space", "useWorldSpace", value = True)
        self.newInput("Boolean", "Use Modifiers", "useModifiers", value = False)
        self.newInput("Scene", "Scene", "scene", hide = True)

        self.newOutput("Vector List", "Vertex Locations", "vertexLocations")
        self.newOutput("Edge Indices List", "Edge Indices", "edgeIndices")
        self.newOutput("Polygon Indices List", "Polygon Indices", "polygonIndices")
        self.newOutput("Vertex List", "Vertices", "vertices")
        self.newOutput("Polygon List", "Polygons", "polygons")
        self.newOutput("String", "Mesh Name", "meshName", hide = True)

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

        yield "meshName = ''"
        yield "if getattr(object, 'type', '') == 'MESH':"
        yield "    mesh = self.getMesh(object, useModifiers, scene)"
        yield "    meshName = mesh.name"

        if isLinked["vertexLocations"] or isLinked["polygons"]:
            yield "    vertexLocations = self.getVertexLocations(mesh, object, useWorldSpace, {})".format(repr(isLinked["vertexLocations"]))
        if isLinked["edgeIndices"]:
            yield "    edgeIndices = self.getEdgeIndices(mesh)"
        if isLinked["polygonIndices"]:
            yield "    polygonIndices = self.getPolygonIndices(mesh)"
        if isLinked["vertices"]:
            yield "    vertices = self.getVertices(mesh, object, useWorldSpace)"
        if isLinked["polygons"]:
            yield "    polygons = self.getPolygons(mesh, vertexLocations, object, useWorldSpace)"

        yield "    self.clearMesh(mesh, useModifiers, scene)"
        yield "else: vertexLocations, edgeIndices, polygonIndices, vertices, polygons = [], [], [], [], []"


    def getMesh(self, object, useModifiers, scene):
        if useModifiers and scene is not None:
            settings = "RENDER" if isRendering() else "PREVIEW"
            return object.to_mesh(scene = scene, apply_modifiers = True, settings = settings)
        return object.data

    def clearMesh(self, mesh, useModifiers, scene):
        if useModifiers and scene is not None: bpy.data.meshes.remove(mesh)


    def getVertexLocations(self, mesh, object, useWorldSpace, copyVertices):
        if useWorldSpace:
            matrix = object.matrix_world
            return [matrix * v.co for v in mesh.vertices]
        else:
            if copyVertices: return [v.co.copy() for v in mesh.vertices]
            else: return [v.co for v in mesh.vertices]

    def getEdgeIndices(self, mesh):
        return [tuple(edge.vertices) for edge in mesh.edges]

    def getPolygonIndices(self, mesh):
        return [tuple(face.vertices) for face in mesh.polygons]

    def getVertices(self, mesh, object, useWorldSpace):
        vertices = []
        if useWorldSpace:
            matrix = object.matrix_world
            rotation = extractRotation(matrix)
            vertices = [Vertex.fromMeshVertexInWorldSpace(meshVertex, matrix, rotation) for meshVertex in mesh.vertices]
        else:
            vertices = [Vertex.fromMeshVertexInLocalSpace(meshVertex) for meshVertex in mesh.vertices]
        return vertices

    def getPolygons(self, mesh, vertexLocations, object, useWorldSpace):
        polygons = []
        if useWorldSpace:
            matrix = object.matrix_world
            rotation = extractRotation(matrix)
            scale = matrix.median_scale
            polygons = [Polygon.fromMeshPolygonInWorldSpace(meshPolygon, vertexLocations, matrix, rotation, scale) for meshPolygon in mesh.polygons]
        else:
            polygons = [Polygon.fromMeshPolygonInLocalSpace(meshPolygon, vertexLocations) for meshPolygon in mesh.polygons]
        return polygons
