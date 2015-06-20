import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling

conversionTypeItems = [
    ("DEGREE_TO_RADIAN", "Degree to Radian", ""),
    ("RADIAN_TO_DEGREE", "Radian to Degree", "")]

class mn_ConvertAngle(Node, AnimationNode):
    bl_idname = "mn_ConvertAngle"
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
        nodeTreeChanged()
    
    conversionType = EnumProperty(name = "Conversion Type", items = conversionTypeItems, update = settingChanged)
    
    def init(self, context):
        forbidCompiling()
        socket1 = self.inputs.new("mn_FloatSocket", "Angle")
        socket2 = self.outputs.new("mn_FloatSocket", "Angle")
        for socket in [socket1, socket2]:
            socket.displayCustomName = True
            socket.uniqueCustomName = False
        self.conversionType = "DEGREE_TO_RADIAN"
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Angle" : "angle"}
    def getOutputSocketNames(self):
        return {"Angle" : "angle"}
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "conversionType", text = "")
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        if self.conversionType == "DEGREE_TO_RADIAN": return "$angle$ = %angle% / 180 * math.pi"
        if self.conversionType == "RADIAN_TO_DEGREE": return "$angle$ = %angle% * 180 / math.pi"
    def getModuleList(self):
        return ["math"]
