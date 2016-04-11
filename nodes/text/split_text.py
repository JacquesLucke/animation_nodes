import bpy, re
from bpy.props import *
from ... events import propertyChanged
from ... tree_info import keepNodeState
from ... base_types.node import AnimationNode

splitTypeItems = [
    ("CHARACTERS", "Characters", "", "", 0),
    ("WORDS", "Words", "", "", 1),
    ("LINES", "Lines", "", "", 2),
    ("REGULAR_EXPRESSION", "Regular Expression", "", "", 3),
    ("N_CHARACTERS", "N Characters", "", "", 4) ]

class SplitTextNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplitTextNode"
    bl_label = "Split Text"
    bl_width_default = 190

    def splitTypeChanges(self, context):
        self.recreateInputs()

    splitType = EnumProperty(
        name = "Split Type", default = "REGULAR_EXPRESSION",
        items = splitTypeItems, update = splitTypeChanges)

    keepDelimiters = BoolProperty(default = False, update = propertyChanged)

    def create(self):
        self.recreateInputs()
        self.newOutput("String List", "Text List", "textList")
        self.newOutput("Integer", "Length", "length")

    def draw(self, layout):
        layout.prop(self, "splitType", text = "")
        if self.splitType == "REGULAR_EXPRESSION":
            layout.prop(self, "keepDelimiters", text = "Keep Delimiters")

    def getExecutionCode(self):
        if self.splitType == "CHARACTERS":
            yield "textList = list(text)"
        elif self.splitType == "WORDS":
            yield "textList = text.split()"
        elif self.splitType == "LINES":
            yield "textList = text.splitlines()"
        elif self.splitType == "REGULAR_EXPRESSION":
            yield "textList = self.splitWithRegularExpression(text, splitBy)"
        elif self.splitType == "N_CHARACTERS":
            yield "textList = self.splitEveryNCharacters(text, n)"
        yield "length = len(textList)"

    def splitWithRegularExpression(self, text, splitBy):
        if splitBy == "": return[text]
        else:
            if self.keepDelimiters: return re.split("("+splitBy+")", text)
            else: return re.split(splitBy, text)

    def splitEveryNCharacters(self, text, n):
        if n <= 0: return []

        textList = list(map(''.join, zip(*([iter(text)] * n))))
        missingChars = len(text) % n
        if missingChars > 0:
            textList.append(text[-missingChars:])
        return textList

    @keepNodeState
    def recreateInputs(self):
        self.inputs.clear()
        self.newInput("String", "Text", "text")
        if self.splitType == "REGULAR_EXPRESSION":
            self.newInput("String", "Split By", "splitBy")
        if self.splitType == "N_CHARACTERS":
            self.newInput("Integer", "N", "n", value = 5, minValue = 1)
