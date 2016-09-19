import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... base_types import AnimationNode

class ParseNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParseNumberNode"
    bl_label = "Parse Number"

    parsingSuccessfull = BoolProperty()

    def create(self):
        self.newInput("Text", "Text", "text")
        self.newOutput("Float", "Number", "number")

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

    def edit(self):
        output = self.outputs[0]
        if output.dataType == "Float":
            if output.shouldBeIntegerSocket(): self.setOutputType("an_IntegerSocket")
        else:
            if output.shouldBeFloatSocket(): self.setOutputType("an_FloatSocket")

    def setOutputType(self, idName):
        if self.outputs[0].bl_idname == idName: return
        self._setOutputType(idName)

    @keepNodeLinks
    def _setOutputType(self, idName):
        self.outputs.clear()
        self.newOutput(idName, "Number", "number")
