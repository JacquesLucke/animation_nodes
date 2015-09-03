import bpy
from bpy.props import *
from ... events import propertyChanged, isRendering
from ... base_types.node import AnimationNode

class ObjectMeshDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectMeshDataNode"
    bl_label = "Object Mesh Data"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_BooleanSocket", "Use World Space", "useWorldSpace").value = True
        self.inputs.new("an_BooleanSocket", "Use Modifiers", "useModifiers").value = False
        self.outputs.new("an_VectorListSocket", "Vertices", "vertices")
        self.outputs.new("an_EdgeIndicesListSocket", "Edge Indices", "edgeIndices")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygon Indices", "polygonIndices")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not (isLinked["vertices"] or
                isLinked["edgeIndices"] or
                isLinked["polygonIndices"]): return ""

        lines = []
        lines.append("if getattr(object, 'type', '') == 'MESH':")
        lines.append("    mesh = self.getMesh(object, useModifiers)")
        if isLinked["vertices"]: lines.append("    vertices = self.getVertices(mesh, object, useWorldSpace)")
        if isLinked["edgeIndices"]: lines.append("    edgeIndices = self.getEdges(mesh)")
        if isLinked["polygonIndices"]: lines.append("    polygonIndices = self.getPolygons(mesh)")
        lines.append("    self.clearMesh(mesh, useModifiers)")
        lines.append("else: vertices, edgeIndices, polygonIndices = [], [], []")
        return lines


    def getMesh(self, object, useModifiers):
        if useModifiers:
            settings = "RENDER" if isRendering() else "PREVIEW"
            return object.to_mesh(scene = bpy.context.scene, apply_modifiers = True, settings = settings)
        return object.data

    def clearMesh(self, mesh, useModifiers):
        if useModifiers: bpy.data.meshes.remove(mesh)


    def getVertices(self, mesh, object, useWorldSpace):
        if useWorldSpace:
            matrix = object.matrix_world
            return [matrix * v.co for v in mesh.vertices]
        else:
            return [v.co.copy() for v in mesh.vertices]

    def getEdges(self, mesh):
        return [tuple(edge.vertices) for edge in mesh.edges]

    def getPolygons(self, mesh):
        return [tuple(face.vertices) for face in mesh.polygons]
