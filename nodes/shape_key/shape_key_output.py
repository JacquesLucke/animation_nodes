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
        self.newInput("Shape Key", "Shape Key", "shapeKey").defaultDrawType = "PROPERTY_ONLY"

        self.newInput("Float", "Value", "value").setRange(0, 1)
        self.newInput("Float", "Slider Min", "sliderMin")
        self.newInput("Float", "Slider Max", "sliderMax")
        self.newInput("String", "Name", "name")
        self.newInput("Boolean", "Mute", "mute")

        self.newOutput("Shape Key", "Shape Key", "shapeKey")

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

    def getBakeCode(self):
        yield "if shapeKey is not None:"
        s = self.inputs
        if s["Value"].isUsed:      yield "    shapeKey.keyframe_insert('value')"
        if s["Slider Min"].isUsed: yield "    shapeKey.keyframe_insert('slider_min')"
        if s["Slider Max"].isUsed: yield "    shapeKey.keyframe_insert('slider_max')"
        if s["Mute"].isUsed:       yield "    shapeKey.keyframe_insert('mute')"
