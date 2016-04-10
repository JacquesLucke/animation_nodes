import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class DebugNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DebugNode"
    bl_label = "Debug"
    dynamicLabelType = "HIDDEN_ONLY"

    printData = BoolProperty(name = "Print to Console", description = "Can be very slow when used often")

    def create(self):
        socket = self.newInput("Generic", "Data", "data", text = "None")
        socket.display.text = True
        socket = self.newInput("Boolean", "Condition", "condition", hide = True)
        socket.showCreateCompareNodeButton = True

    def drawAdvanced(self, layout):
        layout.prop(self, "printData")

    def drawLabel(self):
        return self.inputs[0].text

    def getExecutionCode(self):
        if "Condition" in self.inputs: # support for older nodes
            return "if condition: self.storeDebugData(data)"
        else:
            return "self.storeDebugData(data)"

    def storeDebugData(self, data):
        if isinstance(data, float): text = str(round(data, 5))
        else: text = str(data)

        self.inputs[0].text = text
        if self.printData: print(text)
