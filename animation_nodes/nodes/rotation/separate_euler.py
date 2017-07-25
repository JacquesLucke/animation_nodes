import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types import VectorizedNode
from . c_utils import getAxisListOfEulerList

class SeparateEulerNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_SeparateEulerNode"
    bl_label = "Separate Euler"

    useDegree = BoolProperty(name = "Use Degree", default = False,
        update = executionCodeChanged)

    useList = VectorizedNode.newVectorizeProperty()

    def create(self):
        self.newVectorizedInput("Euler", "useList",
            ("Euler", "euler"), ("Eulers", "eulers"))

        self.newVectorizedOutput("Float", "useList",
            ("X", "x"), ("X", "x"))
        self.newVectorizedOutput("Float", "useList",
            ("Y", "y"), ("Y", "y"))
        self.newVectorizedOutput("Float", "useList",
            ("Z", "z"), ("Z", "z"))

    def draw(self, layout):
        layout.prop(self, "useDegree")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        for i, axis in enumerate("xyz"):
            if isLinked[axis]:
                if self.useList:
                    yield "{0} = self.getAxisList(eulers, '{0}')".format(axis)
                else:
                    yield "{} = euler[{}]".format(axis, i)
                    if self.useDegree:
                        yield "{} *= 180 / math.pi".format(axis)

    def getAxisList(self, eulers, axis):
        return getAxisListOfEulerList(eulers, axis, self.useDegree)

    def getUsedModules(self):
        return ["math"]
