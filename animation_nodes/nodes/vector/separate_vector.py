import bpy
from bpy.props import *
from . list_operation_utils import getAxisListOfVectorList
from ... base_types import AnimationNode, AutoSelectVectorization

class SeparateVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateVectorNode"
    bl_label = "Separate Vector"

    useList = BoolProperty(default = False, update = AnimationNode.updateSockets)

    def create(self):
        self.newInputGroup(self.useList,
            ("Vector", "Vector", "vector"),
            ("Vector List", "Vectors", "vectors"))

        for axis in "XYZ":
            self.newOutputGroup(self.useList,
                ("Float", axis, axis.lower()),
                ("Float List", axis, axis.lower()))

        vectorization = AutoSelectVectorization()
        vectorization.input(self, "useList", self.inputs[0])
        vectorization.output(self, "useList", self.outputs[0])
        vectorization.output(self, "useList", self.outputs[1])
        vectorization.output(self, "useList", self.outputs[2])
        self.newSocketEffect(vectorization)

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        for i, axis in enumerate("xyz"):
            if isLinked[axis]:
                if self.useList:
                    yield "{0} = self.getAxisList(vectors, '{0}')".format(axis)
                else:
                    yield "{} = vector[{}]".format(axis, i)

    def getAxisList(self, vectors, axis):
        return getAxisListOfVectorList(vectors, axis)
