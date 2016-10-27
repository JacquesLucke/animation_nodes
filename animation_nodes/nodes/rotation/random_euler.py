import bpy
import random
from math import radians
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class RandomEulerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomEulerNode"
    bl_label = "Random Euler"

    nodeSeed = IntProperty(name = "Node Seed", update = propertyChanged, max = 1000, min = 0)

    def create(self):
        self.newInput("Integer", "Seed", "seed")
        self.newInput("Float", "Scale", "scale", value = radians(30))
        self.newOutput("Euler", "Euler", "randomEuler")

    def draw(self, layout):
        layout.prop(self, "nodeSeed")

    def getExecutionCode(self):
        yield "randomEuler = Euler(algorithms.random.randomNumberTuple(seed + 45234 * self.nodeSeed, 3, scale))"

    def duplicate(self, sourceNode):
        self.nodeSeed = int(random.random() * 100)
