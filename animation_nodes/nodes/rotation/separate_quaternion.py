import bpy
from bpy.props import *
from ... events import executionCodeChanged
from . c_utils import getAxisListOfQuaternionList
from ... base_types import AnimationNode, VectorizedSocket

class SeparateQuaternionNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_SeparateQuaternionNode"
    bl_label = "Separate Quaternion"

    useList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Quaternion", "useList",
            ("Quaternion", "quaternion"), ("Quaternions", "quaternions")))

        self.newOutput(VectorizedSocket("Float", "useList",
            ("W", "w"), ("W", "w")))
        self.newOutput(VectorizedSocket("Float", "useList",
            ("X", "x"), ("X", "x")))
        self.newOutput(VectorizedSocket("Float", "useList",
            ("Y", "y"), ("Y", "y")))
        self.newOutput(VectorizedSocket("Float", "useList",
            ("Z", "z"), ("Z", "z")))

    def getExecutionCode(self, required):
        for i, axis in enumerate("wxyz"):
            if axis in required:
                if self.useList:
                    yield "{0} = self.getAxisList(quaternions, '{0}')".format(axis)
                else:
                    yield "{} = quaternion[{}]".format(axis, i)

    def getAxisList(self, quaternions, axis):
        return getAxisListOfQuaternionList(quaternions, axis)
