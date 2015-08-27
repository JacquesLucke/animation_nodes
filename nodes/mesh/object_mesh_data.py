import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class ObjectMeshDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectMeshDataNode"
    bl_label = "Object Mesh Data"

    useWorldSpace = BoolProperty(name = "Use World Space", default = True, update = propertyChanged,
        description = "Use real vertex locations (should be turned of when the vertices will be transformed later anyway)")

    useModifiers = BoolProperty(name = "Use Modifiers", default = False, update = propertyChanged,
        description = "Apply modifiers before importing the data")

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object")
        self.outputs.new("an_VectorListSocket", "Vertices", "vertices")
        self.outputs.new("an_EdgeIndicesListSocket", "Edge Indices", "edgeIndices")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygon Indices", "polygonIndices")

    def draw(self, layout):
        layout.prop(self, "useModifiers")
        layout.prop(self, "useWorldSpace")

    def getExecutionCode(self):
        usedOutputs = self.getUsedOutputsDict()
        if not (usedOutputs["vertices"] or
                usedOutputs["edgeIndices"] or
                usedOutputs["polygonIndices"]): return ""

        lines = []
        lines.append("if getattr(object, 'type', '') == 'MESH':")
        lines.append("    mesh = self.getMesh(object)")
        if usedOutputs["vertices"]: lines.append("    vertices = self.getVertices(mesh, object)")
        if usedOutputs["edgeIndices"]: lines.append("    edgeIndices = self.getEdges(mesh)")
        if usedOutputs["polygonIndices"]: lines.append("    polygonIndices = self.getPolygons(mesh)")
        lines.append("    self.clearMesh(mesh)")
        lines.append("else: vertices, edgeIndices, polygonIndices = [], [], []")
        return lines


    def getMesh(self, object):
        if self.useModifiers: return object.to_mesh(scene = bpy.context.scene, apply_modifiers = True, settings = "PREVIEW")
        return object.data

    def clearMesh(self, mesh):
        if self.useModifiers: bpy.data.meshes.remove(mesh)


    def getVertices(self, mesh, object):
        if self.useWorldSpace:
            matrix = object.matrix_world
            return [matrix * v.co for v in mesh.vertices]
        else:
            return [v.co for v in mesh.vertices]

    def getEdges(self, mesh):
        return [tuple(edge.vertices) for edge in mesh.edges]

    def getPolygons(self, mesh):
        return [tuple(face.vertices) for face in mesh.polygons]
