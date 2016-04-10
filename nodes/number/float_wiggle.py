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
        self.newInput("Float", "Seed", "seed")
        self.newInput("Float", "Evolution", "evolution")
        self.newInput("Float", "Speed", "speed", value = 1, minValue = 0)
        self.newInput("Float", "Amplitude", "amplitude", value = 1.0)
        self.newInput("Integer", "Octaves", "octaves", value = 2)
        self.newInput("Float", "Persistance", "persistance", value = 0.3)
        self.newOutput("Float", "Number", "number")

    def draw(self, layout):
        layout.prop(self, "nodeSeed", text = "Node Seed")

    def execute(self, seed, evolution, speed, amplitude, octaves, persistance):
        evolution = evolution * max(speed, 0) / 20 + 2673 * seed + 823 * self.nodeSeed
        noise = perlinNoise(evolution, persistance, octaves)
        return noise * amplitude
