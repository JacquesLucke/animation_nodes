import bpy
from bpy.props import *
from mathutils import Vector
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.perlin_noise import perlinNoise

class VectorWiggleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorWiggleNode"
    bl_label = "Vector Wiggle"

    nodeSeed = IntProperty(update = propertyChanged)

    def create(self):
        self.newInput("Float", "Seed", "seed")
        self.newInput("Float", "Evolution", "evolution")
        self.newInput("Float", "Speed", "speed", value = 1, minValue = 0)
        self.newInput("Vector", "Amplitude", "amplitude", value = [5, 5, 5])
        self.newInput("Integer", "Octaves", "octaves", value = 2)
        self.newInput("Float", "Persistance", "persistance", value = 0.3)
        self.newOutput("Vector", "Vector", "vector")

    def draw(self, layout):
        layout.prop(self, "nodeSeed", text = "Node Seed")

    def execute(self, seed, evolution, speed, amplitude, octaves, persistance):
        vector = Vector()
        evolution = evolution * max(speed, 0) / 20 + 2541 * seed + 823 * self.nodeSeed
        vector[0] = perlinNoise(evolution, persistance, octaves) * amplitude[0]
        evolution += 79
        vector[1] = perlinNoise(evolution, persistance, octaves) * amplitude[1]
        evolution += 263
        vector[2] = perlinNoise(evolution, persistance, octaves) * amplitude[2]
        return vector
