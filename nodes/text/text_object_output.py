import bpy
from bpy.props import *
from ... utils.layout import writeText
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class TextObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextObjectOutputNode"
    bl_label = "Text Object Output"

    errorMessage = StringProperty()

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"

        self.inputs.new("an_StringSocket", "Text", "text")
        self.inputs.new("an_FloatSocket", "Size", "size").value = 1.0
        self.inputs.new("an_FloatSocket", "Extrude", "extrude")
        self.inputs.new("an_FloatSocket", "Shear", "shear")
        self.inputs.new("an_FloatSocket", "Bevel Depth", "bevelDepth")
        self.inputs.new("an_IntegerSocket", "Bevel Resolution", "bevelResolution")

        self.inputs.new("an_FloatSocket", "Letter Spacing", "letterSpacing").value = 1.0
        self.inputs.new("an_FloatSocket", "Word Spacing", "wordSpacing").value = 1.0
        self.inputs.new("an_FloatSocket", "Line Spacing", "lineSpacing").value = 1.0

        self.inputs.new("an_FloatSocket", "X Offset", "xOffset")
        self.inputs.new("an_FloatSocket", "Y Offset", "yOffset")
        self.inputs.new("an_StringSocket", "Align", "align")

        for socket in self.inputs[1:]:
            socket.defaultDrawType = "TEXT_ONLY"
        for socket in self.inputs[4:]:
            socket.hide = True

        self.outputs.new("an_ObjectSocket", "Object", "object")
        self.width = 170

    def draw(self, layout):
        if self.errorMessage != "":
            writeText(layout, self.errorMessage, width = 25, icon = "ERROR")

    def drawAdvanced(self, layout):
        layout.label("This node uses only linked inputs!", icon = "INFO")
        writeText(layout, "Possible values for 'Align' are 'LEFT', 'CENTER', 'RIGHT', 'JUSTIFY' and 'FLUSH'")

    def getExecutionCode(self):
        isLinked = self.getLinkedInputsDict()
        lines = []
        lines.append("if getattr(object, 'type', '') == 'FONT':")
        lines.append("    textObject = object.data")

        if isLinked["text"]: lines.append("    textObject.body = text")
        if isLinked["size"]: lines.append("    textObject.size = size")
        if isLinked["extrude"]: lines.append("    textObject.extrude = extrude")
        if isLinked["shear"]: lines.append("    textObject.shear = shear")
        if isLinked["bevelDepth"]: lines.append("    textObject.bevel_depth = bevelDepth")
        if isLinked["bevelResolution"]: lines.append("    textObject.bevel_resolution = bevelResolution")

        if isLinked["letterSpacing"]: lines.append("    textObject.space_character = letterSpacing")
        if isLinked["wordSpacing"]: lines.append("    textObject.space_word = wordSpacing")
        if isLinked["lineSpacing"]: lines.append("    textObject.space_line = lineSpacing")

        if isLinked["xOffset"]: lines.append("    textObject.offset_x = xOffset")
        if isLinked["yOffset"]: lines.append("    textObject.offset_y = yOffset")
        if isLinked["align"]: lines.append("    self.setAlignment(textObject, align)")

        lines.append("    pass")

        return lines

    def setAlignment(self, textObject, align):
        if align in ("LEFT", "CENTER", "RIGHT", "JUSTIFY", "FLUSH"):
            textObject.align = align
            self.errorMessage = ""
        else:
            self.errorMessage = "The align type is invalid. Look in the advanced panels to see the possibilities."
