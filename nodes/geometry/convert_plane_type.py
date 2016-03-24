import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

conversionTypeItems = [
    ("POINT_NORMAL_TO_MATRIX", "Point/Normal to Matrix", "", "NONE", 0),
    ("MATRIX_TO_POINT_NORMAL", "Matrix to Point/Normal", "", "NONE", 1)]

class ConvertPlaneTypeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertPlaneTypeNode"
    bl_label = "Convert Plane Type"
    bl_width_default = 160
    dynamicLabelType = "HIDDEN_ONLY"

    searchTags = [(name, {"conversionType" : repr(type)}) for type, name, _,_,_ in conversionTypeItems]

    def conversionTypeChanged(self, context):
        self.createSockets()

    conversionType = EnumProperty(name = "Conversion Type", default = "MATRIX_TO_POINT_NORMAL",
        items = conversionTypeItems, update = conversionTypeChanged)

    def create(self):
        self.width = 170
        self.conversionType = "MATRIX_TO_POINT_NORMAL"

    def draw(self, layout):
        layout.prop(self, "conversionType", text = "")

    def drawLabel(self):
        for item in conversionTypeItems:
            if self.conversionType == item[0]: return item[1]

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()):
            return

        if self.conversionType == "POINT_NORMAL_TO_MATRIX":
            yield "if planeNormal.length_squared == 0: planeNormal = mathutils.Vector((0, 0, 1))"
            yield "matrix = mathutils.Matrix.Translation(planePoint) * planeNormal.to_track_quat('Z', 'Y').to_matrix().to_4x4()"
        if self.conversionType == "MATRIX_TO_POINT_NORMAL":
            if isLinked["planePoint"]: yield "planePoint = matrix.to_translation()"
            if isLinked["planeNormal"]: yield "planeNormal = matrix.to_3x3() * mathutils.Vector((0, 0, 1))"

    def getUsedModules(self):
        return ["mathutils"]

    @keepNodeState
    def createSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        if self.conversionType == "POINT_NORMAL_TO_MATRIX":
            self.inputs.new("an_VectorSocket", "Point in Plane", "planePoint")
            self.inputs.new("an_VectorSocket", "Plane Normal", "planeNormal").value = [0, 0, 1]
            self.outputs.new("an_MatrixSocket", "Matrix", "matrix")
        if self.conversionType == "MATRIX_TO_POINT_NORMAL":
            self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
            self.outputs.new("an_VectorSocket", "Point in Plane", "planePoint")
            self.outputs.new("an_VectorSocket", "Plane Normal", "planeNormal")
