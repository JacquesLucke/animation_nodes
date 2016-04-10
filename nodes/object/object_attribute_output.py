import bpy
from bpy.props import *
from ... utils.code import isCodeValid
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class ObjectAttributeOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectAttributeOutputNode"
    bl_label = "Object Attribute Output"
    bl_width_default = 160

    attribute = StringProperty(name = "Attribute", default = "",
        update = executionCodeChanged)

    errorMessage = StringProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Generic", "Value", "value")
        self.newOutput("Object", "Object", "object")

    def draw(self, layout):
        layout.prop(self, "attribute", text = "")
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def getExecutionCode(self):
        code = self.evaluationExpression

        if not isCodeValid(code):
            self.errorMessage = "Invalid Syntax"
            return
        else: self.errorMessage = ""

        yield "try:"
        yield "    self.errorMessage = ''"
        yield "    " + code
        yield "except AttributeError:"
        yield "    if object: self.errorMessage = 'Attribute not found'"
        yield "except KeyError:"
        yield "    if object: self.errorMessage = 'Key not found'"
        yield "except IndexError:"
        yield "    if object: self.errorMessage = 'Index not found'"
        yield "except (ValueError, TypeError):"
        yield "    if object: self.errorMessage = 'Value has a wrong type'"

    @property
    def evaluationExpression(self):
        if self.attribute.startswith("["): return "object" + self.attribute + " = value"
        else: return "object." + self.attribute + " = value"
