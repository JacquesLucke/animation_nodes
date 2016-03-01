import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

fillModeItems = [
    ("LEFT", "Left", "", "TRIA_LEFT", 0),
    ("RIGHT", "Right", "", "TRIA_RIGHT", 1) ]

class FillStringNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FillStringNode"
    bl_label = "Fill Text"

    fillMode = EnumProperty(name = "Fill Mode", default = "LEFT",
        items = fillModeItems, update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_IntegerSocket", "Length", "length")
        self.inputs.new("an_StringSocket", "Text", "text")
        self.inputs.new("an_StringSocket", "Fill", "fill")
        self.outputs.new("an_StringSocket", "Text", "outText")

    def draw(self, layout):
        layout.prop(self, "fillMode", text = "")

    def getExecutionCode(self):
        yield "fillText = ' ' if fill == '' else fill"
        yield "fillText *= max(length, 0)"
        yield "fillText = fillText[:max(length - len(text), 0)]"
        if self.fillMode == "LEFT": yield "outText = fillText + text"
        if self.fillMode == "RIGHT": yield "outText = text + fillText"
