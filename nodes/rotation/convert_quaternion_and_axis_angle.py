import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

conversionTypeItems = [
    ("QUATERNION_TO_AXIS_ANGLE", "Quaternion to Axis Angle", "", "NONE", 0),
    ("AXIS_ANGLE_TO_QUATERNION", "Axis Angle to Quaternion", "", "NONE", 1) ]

class ConvertQuaternionAndAxisAngleNodeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertQuaternionAndAxisAngleNode"
    bl_label = "Convert Quaternion and Axis Angle"

    onlySearchTags = True
    searchTags = [(name, {"conversionType" : repr(type)}) for type, name, _,_,_ in conversionTypeItems]

    def conversionTypeChanged(self, context):
        self.createSockets()
        executionCodeChanged()

    conversionType = EnumProperty(name = "Conversion Type", default = "QUATERNION_TO_AXIS_ANGLE",
        items = conversionTypeItems, update = conversionTypeChanged)
        
    useDegree = BoolProperty(name = "Use Degree", default = False,
        update = executionCodeChanged)

    def create(self):
        self.width = 160
        self.conversionType = "QUATERNION_TO_AXIS_ANGLE"

    def draw(self, layout):
        layout.prop(self, "conversionType", text = "")
        layout.prop(self, "useDegree")

    def drawLabel(self):
        for item in conversionTypeItems:
            if self.conversionType == item[0]: return item[1]

    def getExecutionCode(self):
        if self.conversionType == "QUATERNION_TO_AXIS_ANGLE":
            if self.useDegree: return "axis, angle = quaternion.axis, math.degrees(quaternion.angle)"
            else: return "axis, angle = quaternion.to_axis_angle()"
        if self.conversionType == "AXIS_ANGLE_TO_QUATERNION":
            if self.useDegree: return "quaternion =  mathutils.Quaternion(axis, math.radians(angle))"
            else: return "quaternion =  mathutils.Quaternion(axis, angle)"

    def getUsedModules(self):
        return ["mathutils", "math"]

    def createSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        if self.conversionType == "QUATERNION_TO_AXIS_ANGLE":
            self.inputs.new("an_QuaternionSocket", "Quaternion", "quaternion")
            self.outputs.new("an_VectorSocket", "Axis", "axis")
            self.outputs.new("an_FloatSocket", "Angle", "angle")
        if self.conversionType == "AXIS_ANGLE_TO_QUATERNION":
            self.inputs.new("an_VectorSocket", "Axis", "axis").value = (0, 0, 1)
            self.inputs.new("an_FloatSocket", "Angle", "angle")
            self.outputs.new("an_QuaternionSocket", "Quaternion", "quaternion")
        self.inputs[0].defaultDrawType = "PREFER_PROPERTY"
