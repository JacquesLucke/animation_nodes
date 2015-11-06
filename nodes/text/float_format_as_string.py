import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

signModeItems = [
    ("PLUS", "Plus", "Show [+] on positive numbers", "", 0),
    ("SPACE", "Space", "Show space on positive, to align with -", "", 1),
    ("NONE", "None", "Show only [-] default float behavior", "", 2)]

class FloatFormatNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatFormatNode"
    bl_label = "Float Format" #Float to Text, Float to String

    signMode = EnumProperty(name = "Sign Mode", default = "PLUS",
        items = signModeItems, update = executionCodeChanged)
    
    leadingZeros = BoolProperty(name = "Leading Zeros", default = True,
        description = "Leading Zeros or Spaces (if Off) to fill the length",
        update = executionCodeChanged)

    def create(self):
        self.inputs.new("an_FloatSocket", "Float", "float")
        self.inputs.new("an_IntegerSocket", "Length", "length").value = 8
        self.inputs.new("an_IntegerSocket", "Precision", "precision").value = 3
        self.outputs.new("an_StringSocket", "Text", "outText")

    def draw(self, layout):
        layout.prop(self, "signMode", text = "", icon = "ZOOMIN")
        layout.prop(self, "leadingZeros", text = "Leading Zeros")

    def getExecutionCode(self):
        lines = []
        if self.signMode == "PLUS":  yield "s = '+'"
        if self.signMode == "SPACE": yield "s = ' '"
        if self.signMode == "NONE":  yield "s = '-'"
        if self.leadingZeros: yield "lz = '0'"
        else: yield "lz = ''"
        yield "string = '{:' + s + lz + str(max(length, 0)) + '.' + str(max(precision, 0)) + 'f}'"
        yield "outText = string.format(float)"
