import bpy
from bpy.props import *
from ... utils.code import isCodeValid
from ... base_types import AnimationNode
from ... events import executionCodeChanged

class ObjectAttributeInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectAttributeInputNode"
    bl_label = "Object Attribute Input"
    errorHandlingType = "MESSAGE"

    attribute: StringProperty(name = "Attribute", default = "",
        update = executionCodeChanged)
    evaluateObject: BoolProperty(name = "Evaluate Object", default = True, update = executionCodeChanged,
        description = "Evaluate the object at the active depsgraph. Evaluating the object increases "
                      "execution time but takes into consideration animations, relations, drivers, and"
                      "so on")

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Generic", "Value", "value")

    def draw(self, layout):
        layout.prop(self, "attribute", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "evaluateObject")
        self.invokeFunction(layout, "createAutoExecutionTrigger", text = "Create Execution Trigger")

    def getExecutionCode(self, required):
        code = self.evaluationExpression

        if not isCodeValid(code):
            yield "self.setErrorMessage('Invalid Syntax', show = len(self.attribute.strip()) > 0)"
            yield "value = None"
            return

        yield "try:"
        if self.evaluateObject:
            yield "    evaluatedObject = AN.utils.depsgraph.getEvaluatedID(object)"
        yield "    " + code
        yield "except:"
        yield "    if object: self.setErrorMessage('Attribute not found')"
        yield "    value = None"

    @property
    def evaluationExpression(self):
        if self.attribute.startswith("["):
            return f"value = {self.getAttributeSource()}" + self.attribute
        else:
            return f"value = {self.getAttributeSource()}." + self.attribute

    def getAttributeSource(self):
        return "evaluatedObject" if self.evaluateObject else "object"

    def createAutoExecutionTrigger(self):
        item = self.nodeTree.autoExecution.customTriggers.new("MONITOR_PROPERTY")
        item.idType = "OBJECT"
        item.dataPaths = self.attribute
        item.object = self.inputs["Object"].object
