import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types import AnimationNode

fillModeItems = [
    ("LEFT", "Left", "", "TRIA_LEFT", 0),
    ("RIGHT", "Right", "", "TRIA_RIGHT", 1) ]

class FillStringNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FillStringNode"
    bl_label = "Fill Text"

    fillMode = EnumProperty(name = "Fill Mode", default = "LEFT",
        items = fillModeItems, update = executionCodeChanged)

    def create(self):
        self.newInput("Integer", "Length", "length")
        self.newInput("String", "Text", "text")
        self.newInput("String", "Fill", "fill")
        self.newOutput("String", "Text", "outText")

    def draw(self, layout):
        layout.prop(self, "fillMode", text = "")

    def getExecutionCode(self):
        yield "fillText = ' ' if fill == '' else fill"
        yield "fillText *= max(length - len(text), 0)"
        if self.fillMode == "LEFT": yield "outText = fillText + text"
        if self.fillMode == "RIGHT": yield "outText = text + fillText"
