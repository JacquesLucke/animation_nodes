import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

conversionTypeItems = [
    ("QUATERNION_TO_EULER", "Quaternion to Euler", "", "NONE", 0),
    ("EULER_TO_QUATERNION", "Euler To Quaternion", "", "NONE", 1)]

class ConvertQuaternionAndEulerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertQuaternionAndEulerNode"
    bl_label = "Convert Quaternion and Euler"

    onlySearchTags = True
    searchTags = [
        ("Quaternion to Euler", {"conversionType" : repr("QUATERNION_TO_EULER")}),
        ("Euler to Quaternion", {"conversionType" : repr("EULER_TO_QUATERNION")}) ]

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
        return "Euler to Quaternion" if self.conversionType == "EULER_TO_QUATERNION" else "Quaternion to Euler"

    def getExecutionCode(self):
        if self.conversionType == "QUATERNION_TO_EULER":
            return "euler = quaternion.to_euler('XYZ')"
        if self.conversionType == "EULER_TO_QUATERNION":
            return "quaternion = euler.to_quaternion()"

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
        self.inputs[0].defaultDrawType = "PROPERTY_ONLY"
