import bpy
import random
from bpy.props import *
from libc.limits cimport INT_MAX
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures cimport Vector3DList
from ... algorithms.random cimport uniformRandomNumber

class RandomVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomVectorNode"
    bl_label = "Random Vector"

    nodeSeed = IntProperty(name = "Node Seed", update = propertyChanged, max = 1000, min = 0)

    createList = BoolProperty(name = "Create List", default = False,
        description = "Create a list of random vectors",
        update = AnimationNode.updateSockets)

    def setup(self):
        self.randomizeNodeSeed()

    def create(self):
        if self.createList:
            self.newInput("Integer", "Seed", "seed")
            self.newInput("Integer", "Count", "count", value = 5, minValue = 0)
            self.newInput("Float", "Scale", "scale", value = 2.0)
            self.newOutput("Vector List", "Vectors", "randomVectors")
        else:
            self.newInput("Integer", "Seed", "seed")
            self.newInput("Float", "Scale", "scale", value = 2.0)
            self.newOutput("Vector", "Vector", "randomVector")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row.prop(self, "createList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionCode(self):
        if self.createList:
            yield "randomVectors = self.calcRandomVectors(seed, count, scale)"
        else:
            yield "randomVector = algorithms.random.uniformRandomVectorWithTwoSeeds(seed, self.nodeSeed, scale)"

    def calcRandomVectors(self, seed, count, double scale):
        cdef:
            int length = min(max(count, 0), INT_MAX)
            int startSeed = (seed * 763645 + self.nodeSeed * 2345423) % INT_MAX
            Vector3DList newList = Vector3DList(length = length)
            float* _data = <float*>newList.data
            int i

        for i in range(length * 3):
            _data[i] = uniformRandomNumber(startSeed + i, -scale, scale)

        return newList

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
