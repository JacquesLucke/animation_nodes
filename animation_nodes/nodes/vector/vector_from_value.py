import bpy
from bpy.props import *
from ... base_types import AnimationNode, AutoSelectVectorization

class VectorFromValueNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorFromValueNode"
    bl_label = "Vector from Value"

    useList = BoolProperty(update = AnimationNode.updateSockets)

    def create(self):
        self.newInputGroup(self.useList,
            ("Float", "Value", "value"),
            ("Float List", "Values", "values"))

        self.newOutputGroup(self.useList,
            ("Vector", "Vector", "vector"),
            ("Vector List", "Vectors", "vectors"))

        vectorization = AutoSelectVectorization()
        vectorization.input(self, "useList", self.inputs[0])
        vectorization.output(self, "useList", self.outputs[0])
        self.newSocketEffect(vectorization)

    def getExecutionCode(self):
        if self.useList:
            return "vectors = AN.nodes.vector.list_operation_utils.vectorsFromValues(values)"
        else:
            return "vector = Vector((value, value, value))"
