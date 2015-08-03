import bpy
from ... base_types.node import AnimationNode

lower = "abcdefghijklmnopqrstuvwxyz"
upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
digits = "0123456789"
special = "!$%&/()=?*+#'-_.:,;" + '"'
allChars = lower + upper + digits + special

class CharactersNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CharactersNode"
    bl_label = "Characters"

    inputNames = {}

    outputNames = { "Lower Case" : "lower",
                    "Upper Case" : "upper",
                    "Digits" : "digits",
                    "Special" : "special",
                    "All" : "all" }

    def create(self):
        self.outputs.new("mn_StringSocket", "Lower Case")
        self.outputs.new("mn_StringSocket", "Upper Case")
        self.outputs.new("mn_StringSocket", "Digits")
        self.outputs.new("mn_StringSocket", "Special")
        self.outputs.new("mn_StringSocket", "All")

    def execute(self):
        return lower, upper, digits, special, allChars
