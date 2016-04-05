import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class RandomNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomNumberNode"
    bl_label = "Random Number"

    nodeSeed = IntProperty(update = propertyChanged)

    def create(self):
        self.inputs.new("an_IntegerSocket", "Seed", "seed")
        self.inputs.new("an_FloatSocket", "Min", "minValue").value = 0.0
        self.inputs.new("an_FloatSocket", "Max", "maxValue").value = 1.0
        self.outputs.new("an_FloatSocket", "Number", "number")
        self.randomizeNodeSeed()

    def draw(self, layout):
        layout.prop(self, "nodeSeed", text = "Node Seed")

    def getExecutionCode(self):
        yield "number = random_number_cache[(seed + self.nodeSeed * 123259) % len(random_number_cache)]"
        yield "number = number * (maxValue - minValue) + minValue"

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
