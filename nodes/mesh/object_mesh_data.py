import bpy
from bpy.props import *
from ... data_structures.mesh import Polygon
from ... base_types.node import AnimationNode
from ... events import propertyChanged, isRendering

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
        self.outputs.new("an_PolygonListSocket", "Polygons", "polygons")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not (isLinked["vertexLocations"] or
                isLinked["edgeIndices"] or
                isLinked["polygonIndices"] or
                isLinked["polygons"]): return ""

        lines = []
        lines.append("if getattr(object, 'type', '') == 'MESH':")
        lines.append("    mesh = self.getMesh(object, useModifiers, scene)")

        if isLinked["vertexLocations"] or isLinked["polygons"]:
            lines.append("    vertexLocations = self.getVertexLocations(mesh, object, useWorldSpace, {})".format(repr(isLinked["vertexLocations"])))
        if isLinked["edgeIndices"]:
            lines.append("    edgeIndices = self.getEdgeIndices(mesh)")
        if isLinked["polygonIndices"]:
            lines.append("    polygonIndices = self.getPolygonIndices(mesh)")
        if isLinked["polygons"]:
            lines.append("    polygons = self.getPolygons(mesh, vertexLocations)")
            
        lines.append("    self.clearMesh(mesh, useModifiers, scene)")
        lines.append("else: vertexLocations, edgeIndices, polygonIndices, polygons = [], [], [], []")
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

    def getPolygons(self, mesh, vertexLocations):
        polygons = []

        for meshPolygon in mesh.polygons:
            vertices = [vertexLocations[index].copy() for index in meshPolygon.vertices]
            polygons.append(Polygon(vertices, meshPolygon.normal, meshPolygon.center,
                                    meshPolygon.area, meshPolygon.material_index))
        return polygons
