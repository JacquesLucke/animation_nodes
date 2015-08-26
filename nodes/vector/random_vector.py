import bpy
import random
from bpy.props import *
from mathutils import Vector
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.random import getUniformRandom

class RandomVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomVectorNode"
    bl_label = "Random Vector"

    additionalSeed = IntProperty(update = propertyChanged)

    def create(self):
        self.inputs.new("an_IntegerSocket", "Seed", "seed")
        self.inputs.new("an_FloatSocket", "Max Value", "maxValue").value = 5.0
        self.outputs.new("an_VectorSocket", "Vector", "randomVector")

    def draw(self, layout):
        layout.prop(self, "additionalSeed", text = "Additional Seed")

    def execute(self, seed, maxValue):
        addSeed = 1193 * self.additionalSeed
        return Vector((getUniformRandom(seed + addSeed, -maxValue, maxValue),
                getUniformRandom(seed + 7540 + addSeed, -maxValue, maxValue),
                getUniformRandom(seed + 23450 + addSeed, -maxValue, maxValue)))

    def duplicate(self, sourceNode):
        self.additionalSeed = int(random.random() * 1000)
