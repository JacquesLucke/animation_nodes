import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.perlin_noise import perlinNoise

class FloatWiggleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FloatWiggleNode"
    bl_label = "Number Wiggle"

    nodeSeed = IntProperty(update = propertyChanged)

    def create(self):
        self.inputs.new("an_FloatSocket", "Seed", "seed")
        self.inputs.new("an_FloatSocket", "Evolution", "evolution")
        socket = self.inputs.new("an_FloatSocket", "Speed", "speed")
        socket.value = 1
        socket.minValue = 0
        self.inputs.new("an_FloatSocket", "Amplitude", "amplitude").value = 1.0
        self.inputs.new("an_IntegerSocket", "Octaves", "octaves").value = 2
        self.inputs.new("an_FloatSocket", "Persistance", "persistance").value = 0.3
        self.outputs.new("an_FloatSocket", "Number", "number")

    def draw(self, layout):
        layout.prop(self, "nodeSeed", text = "Node Seed")

    def execute(self, seed, evolution, speed, amplitude, octaves, persistance):
        evolution = evolution * max(speed, 0) / 20 + 2673 * seed + 823 * self.nodeSeed
        noise = perlinNoise(evolution, persistance, octaves)
        return noise * amplitude
