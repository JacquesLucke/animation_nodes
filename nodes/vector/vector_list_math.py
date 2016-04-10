import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

operationItems = [
    ("ADD", "Add", "", "", 0),
    ("AVERAGE", "Average", "", "", 1) ]

class VectorListMathNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorListMathNode"
    bl_label = "Vector List Math"

    operation = EnumProperty(name = "Operation", default = "ADD",
        items = operationItems, update = executionCodeChanged)

    def create(self):
        self.newInput("an_VectorListSocket", "Vector List", "vectors")
        self.newOutput("an_VectorSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def getExecutionCode(self):
        if self.operation in ("ADD", "AVERAGE"):
            yield "result = functools.reduce(operator.add, vectors, mathutils.Vector((0, 0, 0)))"
        if self.operation == "AVERAGE":
            yield "if len(vectors) > 0: result /= len(vectors)"

    def getUsedModules(self):
        return ["operator", "functools", "mathutils"]
