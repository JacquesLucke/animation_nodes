import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... events import executionCodeChanged

conversionTypeItems = [
    ("VECTOR_TO_EULER", "Vector to Euler", "", "NONE", 0),
    ("EULER_TO_VECTOR", "Euler to Vector", "", "NONE", 1)]

class ConvertVectorAndEulerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConvertVectorAndEulerNode"
    bl_label = "Convert Vector and Euler"
    dynamicLabelType = "ALWAYS"

    onlySearchTags = True
    searchTags = [(name, {"conversionType" : repr(type)}) for type, name, _,_,_ in conversionTypeItems]

    useDegree = BoolProperty(name = "Use Degree", default = False,
        update = executionCodeChanged)

    conversionType = EnumProperty(name = "Conversion Type", default = "VECTOR_TO_EULER",
        update = AnimationNode.updateSockets, items = conversionTypeItems)

    def create(self):
        if self.conversionType == "VECTOR_TO_EULER":
            self.newInput("Vector", "Vector", "vector")
            self.newOutput("Euler", "Euler", "euler")
        if self.conversionType == "EULER_TO_VECTOR":
            self.newInput("Euler", "Euler", "euler")
            self.newOutput("Vector", "Vector", "vector")
        self.inputs[0].defaultDrawType = "PROPERTY_ONLY"

    def draw(self, layout):
        layout.prop(self, "conversionType", text = "")
        layout.prop(self, "useDegree")

    def drawLabel(self):
        for item in conversionTypeItems:
            if self.conversionType == item[0]: return item[1]

    def getExecutionCode(self):
        if self.conversionType == "VECTOR_TO_EULER":
            if self.useDegree: return "euler = Euler(vector / 180 * math.pi, 'XYZ')"
            else: return "euler = Euler(vector, 'XYZ')"
        elif self.conversionType == "EULER_TO_VECTOR":
            if self.useDegree: return "vector = Vector(euler) * 180 / math.pi"
            else: return "vector = Vector(euler)"

    def getUsedModules(self):
        return ["math"]
