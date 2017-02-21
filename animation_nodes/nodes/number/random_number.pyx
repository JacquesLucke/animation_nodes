import bpy
import random
from bpy.props import *
from libc.limits cimport INT_MAX
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures cimport DoubleList
from ... algorithms.random cimport uniformRandomNumber

class RandomNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomNumberNode"
    bl_label = "Random Number"
    bl_width_default = 150

    nodeSeed = IntProperty(update = propertyChanged)

    createList = BoolProperty(name = "Create List", default = False,
        description = "Create a list of random numbers",
        update = AnimationNode.refresh)

    def setup(self):
        self.randomizeNodeSeed()

    def create(self):
        if self.createList:
            self.newInput("Integer", "Seed", "seed")
            self.newInput("Integer", "Count", "count", value = 5, minValue = 0)
            self.newInput("Float", "Min", "minValue", value = 0.0)
            self.newInput("Float", "Max", "maxValue", value = 1.0)
            self.newOutput("Float List", "Numbers", "numbers")
        else:
            self.newInput("Integer", "Seed", "seed")
            self.newInput("Float", "Min", "minValue", value = 0.0)
            self.newInput("Float", "Max", "maxValue", value = 1.0)
            self.newOutput("Float", "Number", "number")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row.prop(self, "createList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionCode(self):
        if self.createList:
            yield "numbers = self.calcRandomNumbers(seed, count, minValue, maxValue)"
        else:
            yield "number = algorithms.random.uniformRandomNumberWithTwoSeeds(seed, self.nodeSeed, minValue, maxValue)"

    def calcRandomNumbers(self, seed, count, double minValue, double maxValue):
        cdef:
            int length = min(max(count, 0), INT_MAX)
            int startSeed = (seed * 234253 + self.nodeSeed * 5326534) % INT_MAX
            DoubleList newList = DoubleList(length = length)
            int i

        for i in range(length):
            newList.data[i] = uniformRandomNumber(startSeed + i, minValue, maxValue)

        return newList

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
