import bpy
from bpy.props import *
from ... utils.code import isCodeValid
from ... events import executionCodeChanged
from ... base_types import AnimationNode, VectorizedSocket

class MaterialAttributeOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MaterialAttributeOutputNode"
    bl_label = "Material Attribute Output"
    bl_width_default = 180
    errorHandlingType = "MESSAGE"

    attribute: StringProperty(name = "Attribute", default = "",
        update = executionCodeChanged)

    useMaterialList: VectorizedSocket.newProperty()
    useValueList: BoolProperty(update = AnimationNode.refresh)

    def create(self):
        self.newInput(VectorizedSocket("Material", "useMaterialList",
            ("Material", "material", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Materials", "materials")))

        if self.useValueList and self.useMaterialList:
            self.newInput("Generic List", "Values", "values")
        else:
            self.newInput("Generic", "Value", "value")

        self.newOutput(VectorizedSocket("Material", "useMaterialList",
            ("Material", "material", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Materials", "materials")))

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "attribute", text = "")
        if self.useMaterialList:
            col.prop(self, "useValueList", text = "Multiple Values")

    def getExecutionCode(self, required):
        code = self.evaluationExpression

        if not isCodeValid(code):
            yield "self.setErrorMessage('Invalid Syntax', show = len(self.attribute.strip()) > 0)"
            return

        yield "try:"
        if self.useMaterialList:
            if self.useValueList:
                yield "    _values = [None] if len(values) == 0 else values"
                yield "    _values = itertools.cycle(_values)"
                yield "    for material, value in zip(materials, _values):"
            else:
                yield "    for material in materials:"
            yield "        " + code
        else:
            yield "    " + code
        yield "except AttributeError:"
        yield "    if material: self.setErrorMessage('Attribute not found')"
        yield "except KeyError:"
        yield "    if material: self.setErrorMessage('Key not found')"
        yield "except IndexError:"
        yield "    if material: self.setErrorMessage('Index not found')"
        yield "except (ValueError, TypeError):"
        yield "    if material: self.setErrorMessage('Value has a wrong type')"
        yield "except:"
        yield "    if material:"
        yield "        self.setErrorMessage('Unknown error')"

    @property
    def evaluationExpression(self):
        if self.attribute.startswith("grease_pencil"):
            return "bpy.data.materials[material.name]." + self.attribute + " = value"
        else:
            if self.attribute.startswith("["): return "bpy.data.materials[material.name]" + self.attribute + " = value"
            else: return "bpy.data.materials[material.name]." + self.attribute + " = value"

    def getBakeCode(self):
        if not isCodeValid(self.attribute): return
        if self.useMaterialList:
            yield "for material in materials:"
            yield "    if material is None: continue"
        else:
            yield "if material is not None:"
        yield "    try: material.keyframe_insert({})".format(repr(self.attribute))
        yield "    except: pass"