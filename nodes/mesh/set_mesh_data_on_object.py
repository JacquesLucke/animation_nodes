import bpy
import bmesh
import itertools
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class SetMeshDataOnObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetMeshDataOnObjectNode"
    bl_label = "Set Mesh Data on Object"

    errorMessage = StringProperty()

    checkIndices = BoolProperty(name = "Check Indices", default = True,
        description = "Check that the highest edge or polygon index is below the " +
         "vertex amount (unchecking can crash Blender when the mesh data is invalid)")
         
    checkTupleLengths = BoolProperty(name = "Check Tuple Lengths", default = True,
        description = "Check that edges have two indices and polygons three or more")

    def create(self):
        self.width = 170
        socket = self.inputs.new("an_ObjectSocket", "Object", "object")
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.objectCreationType = "MESH"
        self.inputs.new("an_MeshDataSocket", "Mesh Data", "meshData")
        matSocket = self.inputs.new("an_IntegerListSocket", "Material Indices", "materialIndices")
        matSocket.hide = True
        self.outputs.new("an_ObjectSocket", "Object", "object")

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, icon = "ERROR", width = 20)

    def drawAdvanced(self, layout):
        layout.prop(self, "checkIndices")
        layout.prop(self, "checkTupleLengths")

    def execute(self, object, meshData, materialIndices):
        if object is None: return object
        if object.type != "MESH" or object.mode != "OBJECT":
            self.errorMessage = "Object is not in object mode or is no mesh object"
            return object

        bmesh.new().to_mesh(object.data)

        vertices, edges, polygons = meshData.vertices, meshData.edges, meshData.polygons

        isValidData = meshData.isValid(
            checkTupleLengths = self.checkTupleLengths,
            checkIndices = self.checkIndices)

        if not isValidData:
            self.errorMessage = "The mesh data is invalid"
            return object

        object.data.from_pydata(vertices, edges, polygons)
        isLinked = self.getLinkedInputsDict()
        if isLinked["materialIndices"] and len(materialIndices) > 0:
            for i in range(len(object.data.polygons)): setattr(object.data.polygons[i], "material_index", materialIndices[i%len(materialIndices)])
        object.data.validate()

        self.errorMessage = ""
        return object
