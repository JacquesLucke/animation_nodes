import bpy
from ... base_types.node import AnimationNode

class FloatToStringNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatToStringNode"
    bl_label = "Float to Text"

    def create(self):
        self.newInput("Float", "Number", "number")
        self.newInput("Integer", "Min Length", "minLength", value = 10, minValue = 0)
        self.newInput("Integer", "Decimals", "decimals", value = 3, minValue = 0)
        self.newInput("Boolean", "Insert Sign", "insertSign").value = False
        self.newOutput("String", "Text", "text")

    def execute(self, number, minLength, decimals, insertSign):
        sign = "+" if insertSign else ""

        formatString = "{" + ":{}0{}.{}f".format(sign, max(minLength, 0), max(decimals, 0)) + "}"
        return formatString.format(number)
