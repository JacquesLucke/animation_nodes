import bpy
import random
import numpy as np
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures import QuaternionList
from . c_utils import normalizeQuaternions

class RandomQuaternionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomQuaternionNode"
    bl_label = "Random Quaternion"

    nodeSeed: IntProperty(name = "Node Seed", update = propertyChanged, max = 1000, min = 0)

    createList: BoolProperty(name = "Create List", default = False,
        description = "Create a list of random quaternions",
        update = AnimationNode.refresh)

    def create(self):
        if self.createList:
            self.newInput("Integer", "Seed", "seed")
            self.newInput("Integer", "Count", "count", value = 5, minValue = 0)
            self.newOutput("Quaternion List", "Quaternions", "randomQuaternions")
        else:
            self.newInput("Integer", "Seed", "seed")
            self.newOutput("Quaternion", "Quaternion", "randomQuaternion")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row.prop(self, "createList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionCode(self, required):
        if self.createList:
            yield "randomQuaternions = self.randomQuaternionList(seed + 24523 * self.nodeSeed, count)"
            yield "self.normalizeQuaternionList(randomQuaternions)"
        else:
            yield "randomQuaternion = Quaternion(algorithms.random.randomNumberTuple(seed + 24523 * self.nodeSeed, 4, math.pi))"
            yield "randomQuaternion.normalize()"

    def getUsedModules(self):
        return ["math"]

    def duplicate(self, sourceNode):
        self.nodeSeed = int(random.random() * 100)

    def randomQuaternionList(self, seed, count):
        np.random.seed(seed)
        qs_array = np.random.random_sample((count,4))

        return QuaternionList.fromNumpyArray(qs_array.astype('f').flatten())

    def normalizeQuaternionList(self,quaternions):
        return normalizeQuaternions(quaternions)
