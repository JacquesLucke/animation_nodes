import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class TextObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextObjectOutputNode"
    bl_label = "Text Object Output"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"

        self.inputs.new("an_StringSocket", "Text", "text")
        self.inputs.new("an_FloatSocket", "Extrude", "extrude").setMinMax(0.0, 1e9)
        self.inputs.new("an_FloatSocket", "Shear", "shear").setMinMax(-1.0, 1.0)
        self.inputs.new("an_FloatSocket", "Size", "size").value = 1.0

        self.inputs.new("an_FloatSocket", "Letter Spacing", "letterSpacing").value = 1.0
        self.inputs.new("an_FloatSocket", "Word Spacing", "wordSpacing").value = 1.0
        self.inputs.new("an_FloatSocket", "Line Spacing", "lineSpacing").value = 1.0

        self.inputs.new("an_FloatSocket", "X Offset", "xOffset")
        self.inputs.new("an_FloatSocket", "Y Offset", "yOffset")

        for socket in self.inputs[1:]:
            socket.defaultDrawType = "TEXT_ONLY"
        for socket in self.inputs[4:]:
            socket.hide = True

        self.outputs.new("an_ObjectSocket", "Object", "object")

    def drawAdvanced(self, layout):
        layout.label("This node uses only linked inputs!", icon = "INFO")

    def getExecutionCode(self):
        isLinked = self.getLinkedInputsDict()
        lines = []
        lines.append("if getattr(object, 'type', '') == 'FONT':")
        lines.append("    textObject = object.data")

        if isLinked["text"]: lines.append("    textObject.body = text")
        if isLinked["extrude"]: lines.append("    textObject.extrude = extrude")
        if isLinked["shear"]: lines.append("    textObject.shear = shear")
        if isLinked["size"]: lines.append("    textObject.size = size")

        if isLinked["letterSpacing"]: lines.append("    textObject.space_character = letterSpacing")
        if isLinked["wordSpacing"]: lines.append("    textObject.space_word = wordSpacing")
        if isLinked["lineSpacing"]: lines.append("    textObject.space_line = lineSpacing")

        if isLinked["xOffset"]: lines.append("    textObject.offset_x = xOffset")
        if isLinked["yOffset"]: lines.append("    textObject.offset_y = yOffset")

        lines.append("    pass")

        return lines
