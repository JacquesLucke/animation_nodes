import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... events import executionCodeChanged


conversionTypeItems = [
    ("DEGREE_TO_RADIAN", "Degree to Radian", ""),
    ("RADIAN_TO_DEGREE", "Radian to Degree", "")]


class ConvertAngle(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ConvertAngle"
    bl_label = "Convert Angle"
    isDetermined = True

    inputNames = { "Angle" : "angle" }
    outputNames = { "Angle" : "angle" }

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
        socket1 = self.inputs.new("mn_FloatSocket", "Angle")
        socket2 = self.outputs.new("mn_FloatSocket", "Angle")
        for socket in [socket1, socket2]:
            socket.nameSettings.display = True
            socket.nameSettings.unique = False
        self.conversionType = "DEGREE_TO_RADIAN"

    def draw_buttons(self, context, layout):
        layout.prop(self, "conversionType", text = "")

    def getExecutionCode(self, outputUse):
        if self.conversionType == "DEGREE_TO_RADIAN": return "$angle$ = %angle% / 180 * math.pi"
        if self.conversionType == "RADIAN_TO_DEGREE": return "$angle$ = %angle% * 180 / math.pi"

    def getModuleList(self):
        return ["math"]
