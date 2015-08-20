import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... events import executionCodeChanged

conversionTypeItems = [
    ("DEGREE_TO_RADIAN", "Degree to Radian", ""),
    ("RADIAN_TO_DEGREE", "Radian to Degree", "")]

class ConvertAngle(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertAngle"
    bl_label = "Convert Angle"
    isDetermined = True

    def settingChanged(self, context):
        inSocket = self.inputs["Angle"]
        outSocket = self.outputs["Angle"]
        if self.conversionType == "DEGREE_TO_RADIAN":
            inSocket.customName = "Degree"
            outSocket.customName = "Radian"
        else:
            inSocket.customName = "Radian"
            outSocket.customName = "Degree"
        executionCodeChanged()

    conversionType = EnumProperty(name = "Conversion Type", items = conversionTypeItems, update = settingChanged)

    def create(self):
        socket1 = self.inputs.new("an_FloatSocket", "Angle", "inAngle")
        socket2 = self.outputs.new("an_FloatSocket", "Angle", "outAngle")
        for socket in [socket1, socket2]:
            socket.displayCustomName = True
            socket.nameSettings.unique = False
        self.conversionType = "DEGREE_TO_RADIAN"

    def draw(self, layout):
        layout.prop(self, "conversionType", text = "")

    def getExecutionCode(self):
        if self.conversionType == "DEGREE_TO_RADIAN": return "outAngle = inAngle / 180 * math.pi"
        if self.conversionType == "RADIAN_TO_DEGREE": return "outAngle = inAngle * 180 / math.pi"

    def getModuleList(self):
        return ["math"]
