import bpy
import random
from bpy.props import *
from mathutils import Vector
from ... events import propertyChanged
from ... cache import getUniformRandom
from ... base_types.node import AnimationNode

class RandomVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_RandomVectorNode"
    bl_label = "Random Vector"
    isDetermined = True

    inputNames = { "Seed" : "seed",
                   "Max Values" : "maxValues" }

    outputNames = { "Vector" : "randomVector" }

    additionalSeed = IntProperty(update = propertyChanged)

    def create(self):
        self.inputs.new("mn_IntegerSocket", "Seed")
        self.inputs.new("mn_FloatSocket", "Max Values").value = 5.0
        self.outputs.new("mn_VectorSocket", "Vector")

    def draw_buttons(self, context, layout):
        layout.prop(self, "additionalSeed", text = "Additional Seed")

    def execute(self, seed, maxValues):
        max = maxValues/2
        addSeed = 1193 * self.additionalSeed
        return Vector((getUniformRandom(seed + addSeed, -max, max),
                getUniformRandom(seed + 754 + addSeed, -max, max),
                getUniformRandom(seed + 2345 + addSeed, -max, max)))

    def duplicate(self, sourceNode):
        self.additionalSeed = int(random.random() * 1000)
