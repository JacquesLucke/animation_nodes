import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... cache import getUniformRandom
from ... base_types.node import AnimationNode

class RandomNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomNumberNode"
    bl_label = "Random Number"
    isDetermined = True

    additionalSeed = IntProperty(update = propertyChanged)

    def create(self):
        self.inputs.new("an_IntegerSocket", "Seed", "seed")
        self.inputs.new("an_FloatSocket", "Min", "minValue").value = 0.0
        self.inputs.new("an_FloatSocket", "Max", "maxValue").value = 1.0
        self.outputs.new("an_FloatSocket", "Number", "number")

    def draw(self, layout):
        layout.prop(self, "additionalSeed", text = "Additional Seed")

    def execute(self, seed, minValue, maxValue):
        return getUniformRandom(seed + 1193 * self.additionalSeed, minValue, maxValue)

    def duplicate(self, sourceNode):
        self.additionalSeed = int(random.random() * 1000)
