import bpy
from bpy.props import *
from ... base_types import AnimationNode, AutoSelectFloatOrInteger

class ParseNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParseNumberNode"
    bl_label = "Parse Number"

    parsingSuccessfull = BoolProperty()

    def create(self):
        self.newInput("Text", "Text", "text")
        self.newOutput("Float", "Number", "number")
        self.newSocketEffect(AutoSelectFloatOrInteger(self.outputs[0]))

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
        if self.outputs[0].dataType == "Integer":
            yield "number = int(number)"
