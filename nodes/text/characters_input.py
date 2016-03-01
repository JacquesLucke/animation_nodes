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
        self.outputs.new("an_StringSocket", "Lower Case", "lower")
        self.outputs.new("an_StringSocket", "Upper Case", "upper")
        self.outputs.new("an_StringSocket", "Digits", "digits")
        self.outputs.new("an_StringSocket", "Special", "special")
        self.outputs.new("an_StringSocket", "Line Break", "lineBreak")
        self.outputs.new("an_StringSocket", "All", "all")

    def execute(self):
        return lower, upper, digits, special, lineBreak, allChars
