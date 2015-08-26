import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.perlin_noise import perlinNoise

class FloatWiggleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatWiggleNode"
    bl_label = "Number Wiggle"

    additionalSeed = IntProperty(update = propertyChanged)

    def create(self):
        self.inputs.new("an_FloatSocket", "Seed", "seed")
        self.inputs.new("an_FloatSocket", "Evolution", "evolution")
        self.inputs.new("an_FloatSocket", "Amplitude", "amplitude").value = 1.0
        self.inputs.new("an_IntegerSocket", "Octaves", "octaves").value = 2
        self.inputs.new("an_FloatSocket", "Persistance", "persistance").value = 0.3
        self.outputs.new("an_FloatSocket", "Number", "number")

    def draw(self, layout):
        layout.prop(self, "additionalSeed", text = "Additional Seed")

    def execute(self, seed, evolution, amplitude, octaves, persistance):
        evolution += 2673 * seed + 823 * self.additionalSeed
        noise = perlinNoise(evolution, persistance, octaves)
        return noise * amplitude
