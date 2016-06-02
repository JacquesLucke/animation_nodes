import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... events import executionCodeChanged

conversionTypeItems = [
    ("DEGREE_TO_RADIAN", "Degree to Radian", ""),
    ("RADIAN_TO_DEGREE", "Radian to Degree", "")]

class ConvertAngleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertAngleNode"
    bl_label = "Convert Angle"

    searchTags = [(name, {"conversionType" : repr(type)}) for type, name, _ in conversionTypeItems]

    def settingChanged(self, context):
        inSocket = self.inputs["Angle"]
        outSocket = self.outputs["Angle"]
        if self.conversionType == "DEGREE_TO_RADIAN":
            inSocket.text = "Degree"
            outSocket.text = "Radian"
        else:
            inSocket.text = "Radian"
            outSocket.text = "Degree"
        executionCodeChanged()

    conversionType = EnumProperty(name = "Conversion Type", items = conversionTypeItems, update = settingChanged)

    def create(self):
        socket1 = self.newInput("Float", "Angle", "inAngle")
        socket2 = self.newOutput("Float", "Angle", "outAngle")
        for socket in [socket1, socket2]:
            socket.display.text = True
        self.conversionType = "DEGREE_TO_RADIAN"

    def draw(self, layout):
        layout.prop(self, "conversionType", text = "")

    def getExecutionCode(self):
        if self.conversionType == "DEGREE_TO_RADIAN": return "outAngle = inAngle / 180 * math.pi"
        if self.conversionType == "RADIAN_TO_DEGREE": return "outAngle = inAngle * 180 / math.pi"

    def getUsedModules(self):
        return ["math"]
