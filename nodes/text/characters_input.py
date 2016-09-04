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
        self.newOutput("String", "Lower Case", "lower")
        self.newOutput("String", "Upper Case", "upper")
        self.newOutput("String", "Digits", "digits")
        self.newOutput("String", "Special", "special")
        self.newOutput("String", "Line Break", "lineBreak")
        self.newOutput("String", "All", "all")

    def execute(self):
        return lower, upper, digits, special, lineBreak, allChars
