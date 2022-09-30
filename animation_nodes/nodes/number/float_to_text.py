import bpy
from ... base_types import AnimationNode, VectorizedSocket

class FloatToTextNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_FloatToTextNode"
    bl_label = "Float to Text"

    useList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Float", "useList",
            ("Number", "number"), ("Numbers", "numbers")))
        self.newInput("Integer", "Min Length", "minLength", value = 10, minValue = 0)
        self.newInput("Integer", "Decimals", "decimals", value = 3, minValue = 0)
        self.newInput("Boolean", "Insert Sign", "insertSign").value = False

        self.newOutput(VectorizedSocket("Text", "useList",
            ("Text", "text"), ("Texts", "texts")))

    def getExecutionFunctionName(self):
        if self.useList:
            return "executeList"
        return "executeSingle"

    def executeSingle(self, number, minLength, decimals, insertSign):
        formatString = self.getFormatString(minLength, decimals, insertSign)
        return formatString.format(number)

    def executeList(self, numbers, minLength, decimals, insertSign):
        formatString = self.getFormatString(minLength, decimals, insertSign)
        return [formatString.format(number) for number in numbers]

    def getFormatString(self, minLength, decimals, insertSign):
        sign = "+" if insertSign else ""
        return "{" + ":{}0{}.{}f".format(sign, max(minLength, 0), max(decimals, 0)) + "}"
