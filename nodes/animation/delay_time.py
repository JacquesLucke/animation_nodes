import bpy
from ... base_types.node import AnimationNode

class DelayTimeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DelayTimeNode"
    bl_label = "Delay Time"

    def create(self):
        self.newInput("Float", "Time", "time")
        self.newInput("Float", "Delay", "delay").value = 10
        self.newOutput("Float", "Time", "outTime")

    def getExecutionCode(self):
        return "outTime = time - delay"
