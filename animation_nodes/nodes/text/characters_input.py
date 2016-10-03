import bpy
from ... base_types import AnimationNode

lower = "abcdefghijklmnopqrstuvwxyz"
upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
digits = "0123456789"
special = "!$%&/()=?*+#'-_.:,;" + '"'
lineBreak = "\n"
allChars = lower + upper + digits + special

class CharactersNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CharactersNode"
    bl_label = "Characters"

    def create(self):
        self.newOutput("Text", "Lower Case", "lower")
        self.newOutput("Text", "Upper Case", "upper")
        self.newOutput("Text", "Digits", "digits")
        self.newOutput("Text", "Special", "special")
        self.newOutput("Text", "Line Break", "lineBreak")
        self.newOutput("Text", "All", "all")

    def execute(self):
        return lower, upper, digits, special, lineBreak, allChars
