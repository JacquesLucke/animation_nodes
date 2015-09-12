import bpy
from ... base_types.node import AnimationNode

class DelayTimeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DelayTimeNode"
    bl_label = "Delay Time"

    def create(self):
        self.inputs.new("an_FloatSocket", "Time", "time")
        self.inputs.new("an_FloatSocket", "Delay", "delay")
        self.outputs.new("an_FloatSocket", "Time", "outTime")

    def getExecutionCode(self):
        return "outTime = time - delay"
