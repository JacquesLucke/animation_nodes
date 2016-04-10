import bpy
from ... base_types.node import AnimationNode

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
        self.newOutput("an_StringSocket", "Lower Case", "lower")
        self.newOutput("an_StringSocket", "Upper Case", "upper")
        self.newOutput("an_StringSocket", "Digits", "digits")
        self.newOutput("an_StringSocket", "Special", "special")
        self.newOutput("an_StringSocket", "Line Break", "lineBreak")
        self.newOutput("an_StringSocket", "All", "all")

    def execute(self):
        return lower, upper, digits, special, lineBreak, allChars
