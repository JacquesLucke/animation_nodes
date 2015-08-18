import bpy, re
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

splitTypes = [
    ("Characters", "Characters", ""),
    ("Words", "Words", ""),
    ("Lines", "Lines", ""),
    ("Regexp", "Regexp", "") ]

class SplitText(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplitText"
    bl_label = "Split Text"

    inputNames = { "Text" : "text",
                   "Split By" : "splitBy" }

    outputNames = { "Text List" : "textList",
                    "Length" : "length" }

    def splitTypeChanges(self, context):
        self.setHideProperty()
        propertyChanged()

    splitType = EnumProperty(
        name = "Split Type", default = "Regexp",
        items = splitTypes, update = splitTypeChanges)

    keepDelimiters = BoolProperty(default = False, update = propertyChanged)

    def create(self):
        self.width = 190
        self.inputs.new("an_StringSocket", "Text")
        self.inputs.new("an_StringSocket", "Split By")
        self.outputs.new("an_StringListSocket", "Text List")
        self.outputs.new("an_IntegerSocket", "Length")

    def draw(self, layout):
        layout.prop(self, "splitType", text = "Type")
        if self.splitType == "Regexp":
            layout.prop(self, "keepDelimiters", text = "Keep Delimiters")

    def setHideProperty(self):
        self.inputs["Split By"].hide = not self.splitType == "Regexp"

    def execute(self, text, splitBy):
        textList = []

        if self.splitType == "Characters": textList = list(text)
        elif self.splitType == "Words": textList = text.split()
        elif self.splitType == "Lines": textList = text.split("\n")

        elif self.splitType == "Regexp":
            if splitBy == "": textList = [text]
            else:
                if self.keepDelimiters: textList = re.split("("+splitBy+")", text)
                else: textList = re.split(splitBy, text)

        return textList, len(textList)
