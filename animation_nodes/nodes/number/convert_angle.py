import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

conversionTypeItems = [
    ("DEGREE_TO_RADIAN", "Degree to Radian", "", "NONE", 0),
    ("RADIAN_TO_DEGREE", "Radian to Degree", "", "NONE", 1)]

class ConvertAngleNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_ConvertAngleNode"
    bl_label = "Convert Angle"

    searchTags = [(name, {"conversionType" : repr(type)}) for type, name, *_ in conversionTypeItems]

    conversionType: EnumProperty(name = "Conversion Type", default = "DEGREE_TO_RADIAN",
        items = conversionTypeItems, update = AnimationNode.refresh)

    useList: VectorizedSocket.newProperty()

    def create(self):
        if self.conversionType == "DEGREE_TO_RADIAN":
            self.newInput(VectorizedSocket("Float", "useList", ("Degree", "inAngle"), ("Degrees", "inAngles")))
            self.newOutput(VectorizedSocket("Float", "useList", ("Radian", "outAngle"), ("Radians", "outAngles")))
        elif self.conversionType == "RADIAN_TO_DEGREE":
            self.newInput(VectorizedSocket("Float", "useList", ("Radian", "inAngle"), ("Radians", "inAngles")))
            self.newOutput(VectorizedSocket("Float", "useList", ("Degree", "outAngle"), ("Degrees", "outAngles")))

    def draw(self, layout):
        layout.prop(self, "conversionType", text = "")

    def getExecutionCode(self, required):
        if self.useList:
            if self.conversionType == "DEGREE_TO_RADIAN":
                return "outAngles = AN.nodes.number.c_utils.degreesToRadians(inAngles)"
            if self.conversionType == "RADIAN_TO_DEGREE":
                return "outAngles = AN.nodes.number.c_utils.radiansToDegrees(inAngles)"
        else:
            if self.conversionType == "DEGREE_TO_RADIAN": return "outAngle = inAngle / 180 * math.pi"
            if self.conversionType == "RADIAN_TO_DEGREE": return "outAngle = inAngle * 180 / math.pi"

    def getUsedModules(self):
        return ["math"]
