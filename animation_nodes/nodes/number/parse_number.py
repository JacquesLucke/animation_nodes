import bpy
from bpy.props import *
from ... base_types import AnimationNode, AutoSelectFloatOrInteger

class ParseNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParseNumberNode"
    bl_label = "Parse Number"

    parsingSuccessfull = BoolProperty()

    outputDataType = StringProperty(default = "Float", update = AnimationNode.updateSockets)

    def create(self):
        self.newInput("Text", "Text", "text")
        self.newOutput(self.outputDataType, "Number", "number")
        self.newSocketEffect(AutoSelectFloatOrInteger("outputDataType", self.outputs[0]))

    def draw(self, layout):
        if not self.parsingSuccessfull:
            layout.label("Parsing Error", icon = "ERROR")

    def getExecutionCode(self):
        yield "try:"
        yield "    number = float(text)"
        yield "    self.parsingSuccessfull = True"
        yield "except:"
        yield "    number = 0"
        yield "    self.parsingSuccessfull = False"
        if self.outputDataType == "Integer":
            yield "number = int(number)"
