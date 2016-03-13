import bpy
import bmesh
import itertools
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class SetMeshDataOnObjectNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetMeshDataOnObjectNode"
    bl_label = "Set Mesh Data on Object"
    bl_width_default = 170

    errorMessage = StringProperty()

    checkIndices = BoolProperty(name = "Check Indices", default = True,
        description = "Check that the highest edge or polygon index is below the " +
         "vertex amount (unchecking can crash Blender when the mesh data is invalid)")

    checkTupleLengths = BoolProperty(name = "Check Tuple Lengths", default = True,
        description = "Check that edges have two indices and polygons three or more")

    def create(self):
        socket = self.inputs.new("an_ObjectSocket", "Object", "object")
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.objectCreationType = "MESH"

        self.inputs.new("an_MeshDataSocket", "Mesh Data", "meshData")
        self.inputs.new("an_IntegerListSocket", "Material Indices", "materialIndices").hide = True

        for socket in self.inputs[1:]:
            socket.isUsed = False
            socket.useIsUsedProperty = True

        self.outputs.new("an_ObjectSocket", "Object", "object")

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, icon = "ERROR", width = 20)

    def drawAdvanced(self, layout):
        layout.prop(self, "checkIndices")
        layout.prop(self, "checkTupleLengths")

    def getExecutionCode(self):
        yield "self.errorMessage = ''"
        yield "if self.isValidObject(object):"

        if self.inputs["Mesh Data"].isUsed:                  yield "    self.setMeshData(object, meshData)"
        if self.inputs["Material Indices"].isUsed:           yield "    self.setMaterialIndices(object, materialIndices)"
        if any(socket.isUsed for socket in self.inputs[1:]): yield "    object.data.validate()"
        else: yield "    pass"

    def isValidObject(self, object):
        if object is None: return False
        if object.type != "MESH" or object.mode != "OBJECT":
            self.errorMessage = "Object is not in object mode or is no mesh object"
            return False
        return True

    def setMeshData(self, object, meshData):
        bmesh.new().to_mesh(object.data)

        isValidData = meshData.isValid(
            checkTupleLengths = self.checkTupleLengths,
            checkIndices = self.checkIndices)

        if not isValidData:
            self.errorMessage = "The mesh data is invalid"
            return

        object.data.from_pydata(meshData.vertices, meshData.edges, meshData.polygons)

    def setMaterialIndices(self, object, materialIndices):
        mesh = object.data
        if len(materialIndices) == 0: return
        if len(mesh.polygons) == 0: return
        if any(index < 0 for index in materialIndices):
            self.errorMessage = "Material indices have to be greater or equal to zero"
            return

        allMaterialIndices = list(itertools.islice(itertools.cycle(materialIndices), len(mesh.polygons)))
        mesh.polygons.foreach_set("material_index", allMaterialIndices)
        mesh.polygons[0].material_index = materialIndices[0]
