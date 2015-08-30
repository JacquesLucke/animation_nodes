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

class TextObjectOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_TextObjectOutputNode"
    bl_label = "Text Object Output"

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
        self.setHideProperty()

        self.outputs.new("an_ObjectSocket", "Object", "object")

    def draw(self, layout):
        col = layout.column(align = True)

        for i, option in enumerate(options[:3]):
            col.prop(self, option[0], text = option[1])

    def drawAdvanced(self, layout):
        col = layout.column(align = True)

        for i, option in enumerate(options):
            if i in [4, 7]:
                col.separator()
                col.separator()
            col.prop(self, option[0], text = option[1])

    def setHideProperty(self):
        for option in options:
            self.inputs[option[1]].hide = not getattr(self, option[0])

    def getExecutionCode(self):
        lines = []
        lines.append("if getattr(object, 'type', '') == 'FONT':")
        lines.append("    textObject = object.data")

        if self.useText: lines.append("    textObject.body = text")
        if self.useExtrude: lines.append("    textObject.extrude = extrude")
        if self.useShear: lines.append("    textObject.shear = shear")
        if self.useSize: lines.append("    textObject.size = size")

        if self.useLetterSpacing: lines.append("    textObject.space_character = letterSpacing")
        if self.useWordSpacing: lines.append("    textObject.space_word = wordSpacing")
        if self.useLineSpacing: lines.append("    textObject.space_line = lineSpacing")

        if self.useXOffset: lines.append("    textObject.offset_x = xOffset")
        if self.useYOffset: lines.append("    textObject.offset_y = yOffset")

        lines.append("    pass")

        return lines
