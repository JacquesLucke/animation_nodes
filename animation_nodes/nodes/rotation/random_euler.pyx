import bpy
import random
from bpy.props import *
from math import radians
from libc.limits cimport INT_MAX
from ... math cimport Euler3
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures cimport EulerList
from ... algorithms.random cimport uniformRandomNumber

class RandomEulerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomEulerNode"
    bl_label = "Random Euler"

    nodeSeed = IntProperty(name = "Node Seed", update = propertyChanged, max = 1000, min = 0)

    createList = BoolProperty(name = "Create List", default = False,
        description = "Create a list of random eulers",
        update = AnimationNode.updateSockets)

    def create(self):
        if self.createList:
            self.newInput("Integer", "Seed", "seed")
            self.newInput("Integer", "Count", "count", value = 5, minValue = 0)
            self.newInput("Float", "Scale", "scale", value = radians(30))
            self.newOutput("Euler List", "Eulers", "randomEulers")
        else:
            self.newInput("Integer", "Seed", "seed")
            self.newInput("Float", "Scale", "scale", value = radians(30))
            self.newOutput("Euler", "Euler", "randomEuler")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row.prop(self, "createList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionCode(self):
        yield "randomEuler = Euler(algorithms.random.randomNumberTuple(seed + 45234 * self.nodeSeed, 3, scale))"

    def getExecutionCode(self):
        if self.createList:
            yield "randomEulers = self.calcRandomEulers(seed, count, scale)"
        else:
            yield "randomEuler = Euler(algorithms.random.randomNumberTuple(seed + 45234 * self.nodeSeed, 3, scale))"

    def calcRandomEulers(self, seed, count, double scale):
        cdef:
            int length = min(max(count, 0), INT_MAX)
            int startSeed = (seed * 763645 + self.nodeSeed * 2345423) % INT_MAX
            EulerList newList = EulerList(length = length)
            Euler3* _data = <Euler3*>newList.data
            int i, seedOffset

        for i in range(length):
            seedOffset = i * 3
            _data[i].x = uniformRandomNumber(startSeed + seedOffset + 0, -scale, scale)
            _data[i].y = uniformRandomNumber(startSeed + seedOffset + 1, -scale, scale)
            _data[i].z = uniformRandomNumber(startSeed + seedOffset + 2, -scale, scale)
            _data[i].order = 0

        return newList

    def duplicate(self, sourceNode):
        self.nodeSeed = int(random.random() * 100)
