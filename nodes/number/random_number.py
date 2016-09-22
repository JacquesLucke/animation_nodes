import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class RandomNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomNumberNode"
    bl_label = "Random Number"

    nodeSeed = IntProperty(update = propertyChanged)

    def setup(self):
        self.randomizeNodeSeed()

    def create(self):
        self.newInput("Integer", "Seed", "seed")
        self.newInput("Float", "Min", "minValue", value = 0.0)
        self.newInput("Float", "Max", "maxValue", value = 1.0)
        self.newOutput("Float", "Number", "number")

    def draw(self, layout):
        layout.prop(self, "nodeSeed", text = "Node Seed")

    def getExecutionCode(self):
        yield "number = algorithms.random.uniformRandomNumberWithTwoSeeds(seed, self.nodeSeed, minValue, maxValue)"

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
