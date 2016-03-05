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
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_BooleanSocket", "Use World Space", "useWorldSpace").value = True
        self.inputs.new("an_BooleanSocket", "Use Modifiers", "useModifiers").value = False
        self.inputs.new("an_SceneSocket", "Scene", "scene").hide = True
        self.outputs.new("an_VectorListSocket", "Vertex Locations", "vertexLocations")
        self.outputs.new("an_EdgeIndicesListSocket", "Edge Indices", "edgeIndices")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygon Indices", "polygonIndices")
        self.outputs.new("an_VertexListSocket", "Vertices", "vertices")
        self.outputs.new("an_PolygonListSocket", "Polygons", "polygons")
        self.outputs.new("an_StringSocket", "Mesh Name", "meshName").hide = True

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""

        lines = []
        lines.append("meshName = ''")
        lines.append("if getattr(object, 'type', '') == 'MESH':")
        lines.append("    mesh = self.getMesh(object, useModifiers, scene)")
        lines.append("    meshName = mesh.name")

        if isLinked["vertexLocations"] or isLinked["polygons"]:
            lines.append("    vertexLocations = self.getVertexLocations(mesh, object, useWorldSpace, {})".format(repr(isLinked["vertexLocations"])))
        if isLinked["edgeIndices"]:
            lines.append("    edgeIndices = self.getEdgeIndices(mesh)")
        if isLinked["polygonIndices"]:
            lines.append("    polygonIndices = self.getPolygonIndices(mesh)")
        if isLinked["vertices"]:
            lines.append("    vertices = self.getVertices(mesh, object, useWorldSpace)")
        if isLinked["polygons"]:
            lines.append("    polygons = self.getPolygons(mesh, vertexLocations, object, useWorldSpace)")

        lines.append("    self.clearMesh(mesh, useModifiers, scene)")
        lines.append("else: vertexLocations, edgeIndices, polygonIndices, vertices, polygons = [], [], [], [], []")
        return lines


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
