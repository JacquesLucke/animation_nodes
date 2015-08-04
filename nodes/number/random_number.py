import bpy
import random
from ... events import propertyChanged
from ... cache import getUniformRandom
from ... base_types.node import AnimationNode

class RandomNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomNumberNode"
    bl_label = "Random Number"
    isDetermined = True

    inputNames = { "Seed" : "seed",
                   "Min" : "minValue",
                   "Max" : "maxValue" }

    outputNames = { "Number" : "number" }

    additionalSeed = bpy.props.IntProperty(update = propertyChanged)

    def create(self):
        self.inputs.new("an_IntegerSocket", "Seed")
        self.inputs.new("an_FloatSocket", "Min").value = 0.0
        self.inputs.new("an_FloatSocket", "Max").value = 1.0
        self.outputs.new("an_FloatSocket", "Number")

    def draw_buttons(self, context, layout):
        layout.prop(self, "additionalSeed", text = "Additional Seed")

    def execute(self, seed, minValue, maxValue):
        return getUniformRandom(seed + 1193 * self.additionalSeed, minValue, maxValue)

    def duplicate(self, sourceNode):
        self.additionalSeed = int(random.random() * 1000)
