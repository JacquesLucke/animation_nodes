import bpy, random
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.perlin_noise import perlinNoise


class FloatWiggle(bpy.types.Node, AnimationNode):
    bl_idname = "mn_FloatWiggle"
    bl_label = "Number Wiggle"
    isDetermined = True

    inputNames = { "Seed" : "seed",
                   "Evolution" : "evolution",
                   "Amplitude" : "amplitude",
                   "Octaves" : "octaves",
                   "Persistance" : "persistance" }

    outputNames = { "Number" : "number" }

    additionalSeed = bpy.props.IntProperty(update = propertyChanged)

    def create(self):
        self.inputs.new("mn_FloatSocket", "Seed")
        self.inputs.new("mn_FloatSocket", "Evolution")
        self.inputs.new("mn_FloatSocket", "Amplitude").value = 1.0
        self.inputs.new("mn_IntegerSocket", "Octaves").value = 2
        self.inputs.new("mn_FloatSocket", "Persistance").value = 0.3
        self.outputs.new("mn_FloatSocket", "Number")

    def draw_buttons(self, context, layout):
        layout.prop(self, "additionalSeed", text = "Additional Seed")

    def execute(self, seed, evolution, amplitude, octaves, persistance):
        evolution += 2673 * seed + 823 * self.additionalSeed
        noise = perlinNoise(evolution, persistance, octaves)
        return noise * amplitude
