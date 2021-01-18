import bpy
from ... data_structures import DoubleList
from ... base_types import AnimationNode, VectorizedSocket

class DelayTimeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DelayTimeNode"
    bl_label = "Delay Time"
    dynamicLabelType = "HIDDEN_ONLY"

    useList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Float", "Time", "time")
        self.newInput(VectorizedSocket("Float", "useList",
            ("Delay", "delay",dict(value = 10, minValue = 0)),
            ("Delays", "delays")))
        self.newOutput(VectorizedSocket("Float", "useList",
            ("Time", "outTime"), ("Times", "outTimes")))

    def drawLabel(self):
        delaySocket = self.inputs["Delay"]
        if delaySocket.isUnlinked:
            value = delaySocket.value
            if value == int(value): return "Delay " + str(int(value)) + " Frames"
            else: return "Delay " + str(round(value, 2)) + " Frames"
        else: return "Delay Time"

    def getExecutionCode(self, required):
        if self.useList:
            return "outTimes = DoubleList.fromValues((time - delay) for delay in delays)"
        else:
            return "outTime = time - delay"
