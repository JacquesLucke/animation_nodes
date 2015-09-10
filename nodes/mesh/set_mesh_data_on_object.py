import bpy
import bmesh
import itertools
from bpy.props import *
from ... base_types.node import AnimationNode

class SetMeshDataOnObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetMeshDataOnObjectNode"
    bl_label = "Set Mesh Data on Object"

    errorMessage = StringProperty()
    checkIndices = BoolProperty(name = "Check Indices", default = True,
        description = "Check that the highest edge or polygon index is below the vertex amount")

    def create(self):
        socket = self.inputs.new("an_ObjectSocket", "Object", "object")
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.objectCreationType = "MESH"
        self.inputs.new("an_MeshDataSocket", "Mesh Data", "meshData")
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def drawAdvanced(self, layout):
        layout.prop(self, "checkIndices")

    def execute(self, object, meshData):
        if object is None: return object
        if object.type != "MESH": return object
        if object.mode != "OBJECT": return object
        bmesh.new().to_mesh(object.data)

        vertices, edges, polygons = meshData.vertices, meshData.edges, meshData.polygons
        if self.checkIndices:
            if not self.areIndicesValid(vertices, edges, polygons):
                self.errorMessage = "Indices are invalid"
                return object
                
        object.data.from_pydata(vertices, edges, polygons)
        self.errorMessage = ""
        return object

    def areIndicesValid(self, vertices, edges, polygons):
        maxEdgeIndex = max(itertools.chain([-1], *edges))
        maxPolygonIndex = max(itertools.chain([-1], *polygons))
        return max(maxEdgeIndex, maxPolygonIndex) < len(vertices)
