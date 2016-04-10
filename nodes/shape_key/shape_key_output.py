import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... base_types.node import AnimationNode

class ShapeKeyOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShapeKeyOutputNode"
    bl_label = "Shape Key Output"
    bl_width_default = 160

    errorMessage = StringProperty()

    def create(self):
        self.newInput("an_ShapeKeySocket", "Shape Key", "shapeKey").defaultDrawType = "PROPERTY_ONLY"

        self.newInput("an_FloatSocket", "Value", "value").setRange(0, 1)
        self.newInput("an_FloatSocket", "Slider Min", "sliderMin")
        self.newInput("an_FloatSocket", "Slider Max", "sliderMax")
        self.newInput("an_StringSocket", "Name", "name")
        self.newInput("an_BooleanSocket", "Mute", "mute")

        self.newOutput("an_ShapeKeySocket", "Shape Key", "shapeKey")

        for socket in self.inputs[1:]:
            socket.useIsUsedProperty = True
            socket.isUsed = False
        for socket in self.inputs[2:]:
            socket.hide = True

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    def drawAdvanced(self, layout):
        writeText(layout, "")

    def getExecutionCode(self):
        yield "if shapeKey is not None:"

        s = self.inputs
        if s["Value"].isUsed:      yield "    shapeKey.value = value"
        if s["Slider Min"].isUsed: yield "    shapeKey.slider_min = sliderMin"
        if s["Slider Max"].isUsed: yield "    shapeKey.slider_max = sliderMax"
        if s["Name"].isUsed:       yield "    shapeKey.name = name"
        if s["Mute"].isUsed:       yield "    shapeKey.mute = mute"
        yield "    pass"
