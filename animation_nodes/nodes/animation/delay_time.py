import bpy
from . c_utils import delayTime_Multiple
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualDoubleList, DoubleList

class DelayTimeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DelayTimeNode"
    bl_label = "Delay Time"
    dynamicLabelType = "HIDDEN_ONLY"

    useListA: VectorizedSocket.newProperty()
    useListB: VectorizedSocket.newProperty()
    

    def create(self):
        self.newInput(VectorizedSocket("Float", "useListA",
            ("Time", "time"), ("Times", "times")))
        self.newInput(VectorizedSocket("Float", "useListB",
            ("Delay", "delay", dict(value = 10)),
            ("Delays", "delays")))
        self.newOutput(VectorizedSocket("Float",
            ["useListA", "useListB"],
            ("Time", "outTime"), ("Times", "outTimes")))

    def drawLabel(self):
        delaySocket = self.inputs["Delay"]
        if delaySocket.isUnlinked:
            value = delaySocket.value
            if value == int(value): return "Delay " + str(int(value)) + " Frames"
            else: return "Delay " + str(round(value, 2)) + " Frames"
        else: return "Delay Time"

    def getExecutionCode(self, required):
        if self.useListA and self.useListB:
            return "outTimes = self.executeList_Both(times, delays)"
        elif self.useListA and not self.useListB:
            return "outTimes = self.executeList_Times(times, delay)"
        elif not self.useListA and self.useListB:
            return "outTimes = self.executeList_Delays(time, delays)"
        else:
            return "outTime = time - delay"

    def executeList_Both(self, times, delays):
        virtualA, virtualB = VirtualDoubleList.createMultiple((times, 0), (delays, 0))
        amount = VirtualDoubleList.getMaxRealLength(virtualA, virtualB)

        return delayTime_Multiple(virtualA, virtualB, amount)

    def executeList_Times(self, times, delay):
        delays = DoubleList.fromValue(delay)
        virtualA, virtualB = VirtualDoubleList.createMultiple((times, 0), (delays, 0))
        amount = VirtualDoubleList.getMaxRealLength(virtualA, virtualB)

        return delayTime_Multiple(virtualA, virtualB, amount)

    def executeList_Delays(self, time, delays):
        times = DoubleList.fromValue(time)
        virtualA, virtualB = VirtualDoubleList.createMultiple((times, 0), (delays, 0))
        amount = VirtualDoubleList.getMaxRealLength(virtualA, virtualB)

        return delayTime_Multiple(virtualA, virtualB, amount)
