import bpy
import bmesh
import itertools
from bpy.props import *
from ... utils.layout import writeText
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

meshDataTypeItems = [
    ("MESH_DATA", "Mesh Data", "Mesh Data object that contains only vertex locations, edge indices and polygon indices", "", 0),
    ("BMESH", "BMesh", "BMesh object", "", 1),
    ("VERTICES", "Vertices", "A list of vertex locations; The length of this list has to be equal to the amount of vertices the mesh already has", "", 2) ]

class MeshObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshObjectOutputNode"
    bl_label = "Mesh Object Output"
    bl_width_default = 175
    searchTags = [("Set Mesh Data on Object (old)", {"meshDataType" : repr("MESH_DATA")}),
                  ("Set BMesh on Object (old)", {"meshDataType" : repr("BMESH")}),
                  ("Set Vertices on Object (old)", {"meshDataType" : repr("VERTICES")}) ]

    def meshDataTypeChanged(self, context):
        self.recreateInputs()

    meshDataType = EnumProperty(name = "Mesh Data Type", default = "MESH_DATA",
        items = meshDataTypeItems, update = meshDataTypeChanged)

    checkIndices = BoolProperty(name = "Check Indices", default = True,
        description = "Check that the highest edge or polygon index is below the " +
         "vertex amount (unchecking can crash Blender when the mesh data is invalid)")

    checkTupleLengths = BoolProperty(name = "Check Tuple Lengths", default = True,
        description = "Check that edges have two indices and polygons three or more")

    errorMessage = StringProperty()

    def create(self):
        self.recreateInputs()
        self.newOutput("an_ObjectSocket", "Object", "object")

    @keepNodeState
    def recreateInputs(self):
        self.inputs.clear()

        socket = self.newInput("an_ObjectSocket", "Object", "object")
        socket.defaultDrawType = "PROPERTY_ONLY"
        socket.objectCreationType = "MESH"

        if self.meshDataType == "MESH_DATA":
            self.newInput("an_MeshDataSocket", "Mesh Data", "meshData")
        elif self.meshDataType == "BMESH":
            self.newInput("an_BMeshSocket", "BMesh", "bm")
        elif self.meshDataType == "VERTICES":
            self.newInput("an_VectorListSocket", "Vertices", "vertices")

        self.newInput("an_IntegerListSocket", "Material Indices", "materialIndices")

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False

    def draw(self, layout):
        if not self.meshInputSocket.hide:
            layout.prop(self, "meshDataType", text = "Type")
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    @property
    def meshInputSocket(self):
        if self.meshDataType == "MESH_DATA": return self.inputs["Mesh Data"]
        if self.meshDataType == "BMESH": return self.inputs["BMesh"]
        if self.meshDataType == "VERTICES": return self.inputs["Vertices"]

    def drawAdvanced(self, layout):
        layout.prop(self, "checkIndices")
        layout.prop(self, "checkTupleLengths")

    def getExecutionCode(self):
        yield "self.errorMessage = ''"
        yield "if self.isValidObject(object):"
        yield "    mesh = object.data"

        s = self.inputs

        if self.meshDataType == "MESH_DATA":
            if s["Mesh Data"].isUsed:    yield "    self.setMeshData(mesh, meshData)"
        elif self.meshDataType == "BMESH":
            if s["BMesh"].isUsed:        yield "    self.setBMesh(mesh, bm)"
        elif self.meshDataType == "VERTICES":
            if s["Vertices"].isUsed:     yield "    self.setVertices(mesh, vertices)"

        if s["Material Indices"].isUsed: yield "    self.setMaterialIndices(mesh, materialIndices)"

    def isValidObject(self, object):
        if object is None: return False
        if object.type != "MESH" or object.mode != "OBJECT":
            self.errorMessage = "Object is not in object mode or is no mesh object"
            return False
        return True

    def setMeshData(self, mesh, meshData):
        # clear existing mesh
        bmesh.new().to_mesh(mesh)

        isValidData = meshData.isValid(
            checkTupleLengths = self.checkTupleLengths,
            checkIndices = self.checkIndices)

        if isValidData:
            mesh.from_pydata(meshData.vertices, meshData.edges, meshData.polygons)
        else:
            self.errorMessage = "The mesh data is invalid"

    def setBMesh(self, mesh, bm):
        bm.to_mesh(mesh)

    def setVertices(self, mesh, vertices):
        if len(mesh.vertices) != len(vertices):
            self.errorMessage = "The vertex amounts are not equal"
            return object

        flatVertices = list(itertools.chain.from_iterable(vertices))
        mesh.vertices.foreach_set("co", flatVertices)
        mesh.update()

    def setMaterialIndices(self, mesh, materialIndices):
        if len(materialIndices) == 0: return
        if len(mesh.polygons) == 0: return
        if any(index < 0 for index in materialIndices):
            self.errorMessage = "Material indices have to be greater or equal to zero"
            return

        allMaterialIndices = list(itertools.islice(itertools.cycle(materialIndices), len(mesh.polygons)))
        mesh.polygons.foreach_set("material_index", allMaterialIndices)
        mesh.polygons[0].material_index = materialIndices[0]
