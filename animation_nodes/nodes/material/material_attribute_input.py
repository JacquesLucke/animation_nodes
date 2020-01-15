import bpy
from bpy.props import *
from ... utils.code import isCodeValid
from ... events import executionCodeChanged
from ... base_types import AnimationNode

class MaterialAttributeInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MaterialAttributeInputNode"
    bl_label = "Material Attribute Input"
    bl_width_default = 180
    errorHandlingType = "MESSAGE"

    attribute: StringProperty(name = "Attribute", default = "",
        update = executionCodeChanged)   

    def create(self):
        self.newInput("Material", "Material", "material", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Generic", "Value", "value")

    def draw(self, layout):
        layout.prop(self, "attribute", text = "")

    def getExecutionCode(self, required):
        code = self.evaluationExpression

        if not isCodeValid(code):
            yield "self.setErrorMessage('Invalid Syntax', show = len(self.attribute.strip()) > 0)"
            yield "value = None"
            return

        yield "try:"
        yield "    " + code
        yield "except:"
        yield "    if material: self.setErrorMessage('Attribute not found')"
        yield "    value = None"

    @property
    def evaluationExpression(self):
        if self.attribute.startswith("grease_pencil"):
            return "value = bpy.data.materials[material.name]." + self.attribute
        else:
            if self.attribute.startswith("["): return "value = bpy.data.materials[material.name]" + self.attribute
            else: return "value = bpy.data.materials[material.name]." + self.attribute