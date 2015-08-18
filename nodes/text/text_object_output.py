import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

options = [ ("useText", "Text"),
            ("useExtrude", "Extrude"),
            ("useShear", "Shear"),
            ("useSize", "Size"),
            ("useLetterSpacing", "Letter Spacing"),
            ("useWordSpacing", "Word Spacing"),
            ("useLineSpacing", "Line Spacing"),
            ("useXOffset", "X Offset"),
            ("useYOffset", "Y Offset") ]

class TextOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextOutputNode"
    bl_label = "Text Output"

    inputNames = { "Object" : "object",
                   "Text" : "text",
                   "Size" : "size",
                   "Shear" : "shear",
                   "Extrude" : "extrude",
                   "Letter Spacing" : "letterSpacing",
                   "Word Spacing" : "wordSpacing",
                   "Line Spacing" : "lineSpacing",
                   "X Offset" : "xOffset",
                   "Y Offset" : "yOffset" }

    outputNames = { "Object": "object" }

    def usePropertyChanged(self, context):
        self.setHideProperty()
        executionCodeChanged()

    useText = BoolProperty(default = True, update = usePropertyChanged)
    useExtrude = BoolProperty(default = False, update = usePropertyChanged)
    useShear = BoolProperty(default = False, update = usePropertyChanged)
    useSize = BoolProperty(default = False, update = usePropertyChanged)

    useLetterSpacing = BoolProperty(default = False, update = usePropertyChanged)
    useWordSpacing = BoolProperty(default = False, update = usePropertyChanged)
    useLineSpacing = BoolProperty(default = False, update = usePropertyChanged)

    useXOffset = BoolProperty(default = False, update = usePropertyChanged)
    useYOffset = BoolProperty(default = False, update = usePropertyChanged)

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object").showName = False

        self.inputs.new("an_StringSocket", "Text")
        self.inputs.new("an_FloatSocket", "Extrude").value = 0.0
        self.inputs.new("an_FloatSocket", "Shear").value = 0.0
        self.inputs.new("an_FloatSocket", "Size").value = 1.0

        self.inputs.new("an_FloatSocket", "Letter Spacing").value = 1.0
        self.inputs.new("an_FloatSocket", "Word Spacing").value = 1.0
        self.inputs.new("an_FloatSocket", "Line Spacing").value = 1.0

        self.inputs.new("an_FloatSocket", "X Offset").value = 0.0
        self.inputs.new("an_FloatSocket", "Y Offset").value = 0.0
        self.setHideProperty()

        self.outputs.new("an_ObjectSocket", "Object")

    def draw(self, layout):
        col = layout.column(align = True)

        for i, option in enumerate(options[:3]):
            col.prop(self, option[0], text = option[1])

    def drawAdvanced(self, layout):
        col = layout.column(align = True)

        for i, option in enumerate(options):
            if i in [4, 7]: col.separator(); col.separator()
            col.prop(self, option[0], text = option[1])

    def setHideProperty(self):
        for option in options:
            self.inputs[option[1]].hide = not getattr(self, option[0])

    def getExecutionCode(self, usedOutputs):
        codeLines = []
        codeLines.append("$object$ = %object%")
        codeLines.append("if %object% is not None:")
        codeLines.append("    textObject = None")
        codeLines.append("    if %object%.type == 'FONT': textObject = %object%.data")
        codeLines.append("    if textObject is not None:")

        if self.useText: codeLines.append(" "*8 + "textObject.body = %text%")
        if self.useExtrude: codeLines.append(" "*8 + "textObject.extrude = %extrude%")
        if self.useShear: codeLines.append(" "*8 + "textObject.shear = %shear%")
        if self.useSize: codeLines.append(" "*8 + "textObject.size = %size%")

        if self.useLetterSpacing: codeLines.append(" "*8 + "textObject.space_character = %letterSpacing%")
        if self.useWordSpacing: codeLines.append(" "*8 + "textObject.space_word = %wordSpacing%")
        if self.useLineSpacing: codeLines.append(" "*8 + "textObject.space_line = %lineSpacing%")

        if self.useXOffset: codeLines.append(" "*8 + "textObject.offset_x = %xOffset%")
        if self.useYOffset: codeLines.append(" "*8 + "textObject.offset_y = %yOffset%")

        codeLines.append(" "*8 + "pass")

        return "\n".join(codeLines)
