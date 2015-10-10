import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

conversionTypeItems = [
    ("QUATERNION_TO_EULER", "Quaternion to Euler", "", "NONE", 0),
    ("EULER_TO_QUATERNION", "Euler to Quaternion", "", "NONE", 1),
    ("QUATERNION_TO_MATRIX", "Quaternion to Matrix", "", "NONE", 2),
    ("MATRIX_TO_QUATERNION", "Matrix to Quaternion", "", "NONE", 3),
    ("EULER_TO_MATRIX", "Euler to Matrix", "", "NONE", 4),
    ("MATRIX_TO_EULER", "Matrix to Euler", "", "NONE", 5)]

class ConvertRotationsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertRotationsNode"
    bl_label = "Convert Rotations"

    onlySearchTags = True
    searchTags = [
        ("Quaternion to Euler", {"conversionType" : repr("QUATERNION_TO_EULER")}),
        ("Euler to Quaternion", {"conversionType" : repr("EULER_TO_QUATERNION")}),
        ("Quaternion to Matrix", {"conversionType" : repr("QUATERNION_TO_MATRIX")}),
        ("Matrix to Quaternion", {"conversionType" : repr("MATRIX_TO_QUATERNION")}),
        ("Euler to Matrix", {"conversionType" : repr("EULER_TO_MATRIX")}),
        ("Matrix to Euler", {"conversionType" : repr("MATRIX_TO_EULER")}) ]

    def conversionTypeChanged(self, context):
        self.createSockets()
        executionCodeChanged()

    conversionType = EnumProperty(name = "Conversion Type", default = "QUATERNION_TO_EULER",
        items = conversionTypeItems, update = conversionTypeChanged)

    def create(self):
        self.width = 160
        self.conversionType = "QUATERNION_TO_EULER"

    def draw(self, layout):
        layout.prop(self, "conversionType", text = "")

    def drawLabel(self):
        for item in conversionTypeItems:
            if self.conversionType == item[0]: return item[1]

    def getExecutionCode(self):
        if self.conversionType == "QUATERNION_TO_EULER":
            return "euler = quaternion.to_euler('XYZ')"
        if self.conversionType == "EULER_TO_QUATERNION":
            return "quaternion = euler.to_quaternion()"
        
        if self.conversionType == "QUATERNION_TO_MATRIX":
            return "matrix = quaternion.to_matrix().to_4x4()"
        if self.conversionType == "MATRIX_TO_QUATERNION":
            return "quaternion = matrix.to_quaternion()"
        
        if self.conversionType == "EULER_TO_MATRIX":
            return "matrix = euler.to_matrix().to_4x4()"
        if self.conversionType == "MATRIX_TO_EULER":
            return "euler = matrix.to_euler('XYZ')"

    def getUsedModules(self):
        return ["mathutils"]

    def createSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        if self.conversionType == "QUATERNION_TO_EULER":
            self.inputs.new("an_QuaternionSocket", "Quaternion", "quaternion")
            self.outputs.new("an_EulerSocket", "Euler", "euler")
        if self.conversionType == "EULER_TO_QUATERNION":
            self.inputs.new("an_EulerSocket", "Euler", "euler")
            self.outputs.new("an_QuaternionSocket", "Quaternion", "quaternion")
            
        if self.conversionType == "QUATERNION_TO_MATRIX":
            self.inputs.new("an_QuaternionSocket", "Quaternion", "quaternion")
            self.outputs.new("an_MatrixSocket", "Matrix", "matrix")
        if self.conversionType == "MATRIX_TO_QUATERNION":
            self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
            self.outputs.new("an_QuaternionSocket", "Quaternion", "quaternion")
            
        if self.conversionType == "EULER_TO_MATRIX":
            self.inputs.new("an_EulerSocket", "Euler", "euler")
            self.outputs.new("an_MatrixSocket", "Matrix", "matrix")
        if self.conversionType == "MATRIX_TO_EULER":
            self.inputs.new("an_MatrixSocket", "Matrix", "matrix")
            self.outputs.new("an_EulerSocket", "Euler", "euler")
            
        self.inputs[0].defaultDrawType = "PROPERTY_ONLY"
