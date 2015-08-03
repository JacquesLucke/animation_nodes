import bpy
from ... events import propertyChanged
from ... mn_cache import getUniformRandom
from ... base_types.node import AnimationNode

class RandomNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_RandomNumberNode"
    bl_label = "Random Number"
    isDetermined = True

    inputNames = { "Seed" : "seed",
                   "Min" : "minValue",
                   "Max" : "maxValue" }

    outputNames = { "Number" : "number" }

    additionalSeed = bpy.props.IntProperty(update = propertyChanged)

    def create(self):
        self.inputs.new("mn_IntegerSocket", "Seed")
        self.inputs.new("mn_FloatSocket", "Min").value = 0.0
        self.inputs.new("mn_FloatSocket", "Max").value = 1.0
        self.outputs.new("mn_FloatSocket", "Number")

    def draw_buttons(self, context, layout):
        layout.prop(self, "additionalSeed", text = "Additional Seed")

    def execute(self, seed, minValue, maxValue):
        return getUniformRandom(seed + 1193 * self.additionalSeed, minValue, maxValue)

    def copy(self, node):
        self.additionalSeed = int(random.random()*1000)
