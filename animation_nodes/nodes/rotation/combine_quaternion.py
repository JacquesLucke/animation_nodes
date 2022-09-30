import bpy
from bpy.props import *
from . c_utils import combineQuaternionList
from ... events import executionCodeChanged
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class CombineQuaternionNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_CombineQuaternionNode"
    bl_label = "Combine Quaternion"

    useListW: VectorizedSocket.newProperty()
    useListX: VectorizedSocket.newProperty()
    useListY: VectorizedSocket.newProperty()
    useListZ: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Float", "useListW", ("W", "w", dict(value = 1)), ("W", "w")))
        self.newInput(VectorizedSocket("Float", "useListX", ("X", "x"), ("X", "x")))
        self.newInput(VectorizedSocket("Float", "useListY", ("Y", "y"), ("Y", "y")))
        self.newInput(VectorizedSocket("Float", "useListZ", ("Z", "z"), ("Z", "z")))

        self.newOutput(VectorizedSocket("Quaternion",
            ["useListW", "useListX", "useListY", "useListZ"],
            ("Quaternion", "quaternion"), ("Quaternions", "quaternions")))

    def getExecutionCode(self, required):
        if self.generatesList:
            yield "quaternions = self.createQuaternionList(w, x, y, z)"
        else:
            yield "quaternion = Quaternion((w, x, y, z)).normalized()"

    def createQuaternionList(self, w, x, y, z):
        w, x, y, z = VirtualDoubleList.createMultiple((w, 0), (x, 0), (y, 0), (z, 0))
        amount = VirtualDoubleList.getMaxRealLength(w, x, y, z)
        return combineQuaternionList(amount, w, x, y, z)

    @property
    def generatesList(self):
        return any((self.useListW, self.useListX, self.useListY, self.useListZ))
