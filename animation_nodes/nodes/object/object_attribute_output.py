import bpy
from bpy.props import *
from ... utils.code import isCodeValid
from ... events import executionCodeChanged
from ... base_types import AnimationNode, AutoSelectVectorization

class ObjectAttributeOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectAttributeOutputNode"
    bl_label = "Object Attribute Output"
    bl_width_default = 175

    attribute = StringProperty(name = "Attribute", default = "",
        update = executionCodeChanged)

    useObjectList = BoolProperty(default = False, update = AnimationNode.refresh)
    useValueList = BoolProperty(default = False, update = AnimationNode.refresh)

    errorMessage = StringProperty()

    def create(self):
        self.newInputGroup(self.useObjectList,
            ("Object", "Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Object List", "Objects", "objects"))

        self.newInputGroup(self.useValueList and self.useObjectList,
            ("Generic", "Value", "value"),
            ("Generic List", "Values", "values"))

        self.newOutputGroup(self.useObjectList,
            ("Object", "Object", "object"),
            ("Object List", "Objects", "objects"))

        vectorization = AutoSelectVectorization()
        vectorization.input(self, "useObjectList", self.inputs[0])
        vectorization.output(self, "useObjectList", self.outputs[0])
        self.newSocketEffect(vectorization)

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "attribute", text = "")
        if self.useObjectList:
            col.prop(self, "useValueList", text = "Multiple Values")
        if self.errorMessage != "" and self.attribute != "":
            layout.label(self.errorMessage, icon = "ERROR")

    def getExecutionCode(self):
        code = self.evaluationExpression

        if not isCodeValid(code):
            self.errorMessage = "Invalid Syntax"
            return
        else: self.errorMessage = ""

        yield "try:"
        yield "    self.errorMessage = ''"
        if self.useObjectList:
            if self.useValueList:
                yield "    if len(objects) != len(values):"
                yield "        self.errorMessage = 'Lists have different length'"
                yield "        raise Exception()"
                yield "    for object, value in zip(objects, values):"
            else:
                yield "    for object in objects:"
            yield "        " + code
        else:
            yield "    " + code
        yield "except AttributeError:"
        yield "    if object: self.errorMessage = 'Attribute not found'"
        yield "except KeyError:"
        yield "    if object: self.errorMessage = 'Key not found'"
        yield "except IndexError:"
        yield "    if object: self.errorMessage = 'Index not found'"
        yield "except (ValueError, TypeError):"
        yield "    if object: self.errorMessage = 'Value has a wrong type'"
        yield "except:"
        yield "    if object and self.errorMessage == '':"
        yield "        self.errorMessage = 'Unknown error'"

    @property
    def evaluationExpression(self):
        if self.attribute.startswith("["): return "object" + self.attribute + " = value"
        else: return "object." + self.attribute + " = value"

    def getBakeCode(self):
        if not isCodeValid(self.attribute): return
        if self.useObjectList:
            yield "for object in objects:"
            yield "    if object is None: continue"
        else:
            yield "if object is not None:"
        yield "    try: object.keyframe_insert({})".format(repr(self.attribute))
        yield "    except: pass"
