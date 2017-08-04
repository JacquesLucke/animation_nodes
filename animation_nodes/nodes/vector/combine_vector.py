import bpy
from bpy.props import *
from . c_utils import combineVectorList
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class CombineVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CombineVectorNode"
    bl_label = "Combine Vector"
    dynamicLabelType = "HIDDEN_ONLY"

    useListX = VectorizedSocket.newProperty()
    useListY = VectorizedSocket.newProperty()
    useListZ = VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Float", "useListX", ("X", "x"), ("X", "x")))
        self.newInput(VectorizedSocket("Float", "useListY", ("Y", "y"), ("Y", "y")))
        self.newInput(VectorizedSocket("Float", "useListZ", ("Z", "z"), ("Z", "z")))

        self.newOutput(VectorizedSocket("Vector",
            ["useListX", "useListY", "useListZ"],
            ("Vector", "vector"), ("Vectors", "vectors")))

    def drawLabel(self):
        label = "<X, Y, Z>"
        for socket in self.inputs:
            axis = socket.name
            if not getattr(self, "useList" + axis) and not socket.isLinked:
                label = label.replace(axis, str(round(socket.value, 4)))
        return label

    def getExecutionCode(self, required):
        if self.generatesList:
            yield "vectors = self.createVectorList(x, y, z)"
        else:
            yield "vector = Vector((x, y, z))"

    def createVectorList(self, x, y, z):
        _x = VirtualDoubleList.fromListOrElement(x, 0)
        _y = VirtualDoubleList.fromListOrElement(y, 0)
        _z = VirtualDoubleList.fromListOrElement(z, 0)
        amount = VirtualDoubleList.getMaxRealLength(_x, _y, _z)
        return combineVectorList(amount, _x, _y, _z)

    @property
    def generatesList(self):
        return any((self.useListX, self.useListY, self.useListZ))
