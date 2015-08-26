import bpy
from bpy.props import *
from ... sockets.info import toIdName
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class MixDataNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MixDataNode"
    bl_label = "Mix"

    onlySearchTags = True
    searchTags = [ ("Mix Matrices", {"dataType" : repr("Matrix")}),
                   ("Mix Vectors", {"dataType" : repr("Vector")}),
                   ("Mix Floats", {"dataType" : repr("Float")}),
                   ("Mix Colors", {"dataType" : repr("Color")}) ]

    def dataTypeChanged(self, context):
        self.generateSockets()
        executionCodeChanged()

    dataType = StringProperty(default = "Float", update = dataTypeChanged)
    clampFactor = BoolProperty(name = "Clamp Factor",
        description = "Clamp factor between 0 and 1",
        default = False, update = executionCodeChanged)

    def create(self):
        self.generateSockets()

    def draw(self, layout):
        layout.prop(self, "clampFactor")

    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        idName = toIdName(self.dataType)
        self.inputs.new("an_FloatSocket", "Factor", "factor")
        self.inputs.new(idName, "A", "a")
        self.inputs.new(idName, "B", "b")
        self.outputs.new(idName, "Output", "output")

    def getExecutionCode(self):
        lines = []
        if self.clampFactor: lines.append("f = min(max(factor, 0.0), 1.0)")
        else: lines.append("f = factor")
        if self.dataType in ("Float", "Vector"): lines.append("output = a * (1 - f) + b * f")
        if self.dataType == "Matrix": lines.append("output = a.lerp(b, f)")
        if self.dataType == "Color": lines.append("output = [v1 * (1 - f) + v2 * f for v1, v2 in zip(a, b)]")
        return lines
