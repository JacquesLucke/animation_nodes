import bpy
from bpy.props import *
from mathutils import Quaternion
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.perlin_noise import perlinNoise

class QuaternionWiggleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_QuaternionWiggleNode"
    bl_label = "Quaternion Wiggle"

    nodeSeed = IntProperty(update = propertyChanged)

    def create(self):
        self.newInput("Float", "Seed", "seed")
        self.newInput("Float", "Evolution", "evolution")
        self.newInput("Float", "Speed", "speed", value = 1, minValue = 0)
        self.newInput("Quaternion", "Amplitude", "amplitude", value = [1, 0.3, 0.3, 0.3])
        self.newInput("Integer", "Octaves", "octaves", value = 2)
        self.newInput("Float", "Persistance", "persistance", value = 0.3)
        self.newOutput("Quaternion", "Quaternion", "quaternion")

    def draw(self, layout):
        layout.prop(self, "nodeSeed", text = "Node Seed")

    def execute(self, seed, evolution, speed, amplitude, octaves, persistance):
        quaternion = Quaternion()
        quaternion[0] = amplitude[0]
        evolution = evolution * max(speed, 0) / 20 + 2541 * seed + 823 * self.nodeSeed
        quaternion[1] = perlinNoise(evolution, persistance, octaves) * amplitude[1]
        evolution += 79
        quaternion[2] = perlinNoise(evolution, persistance, octaves) * amplitude[2]
        evolution += 263
        quaternion[3] = perlinNoise(evolution, persistance, octaves) * amplitude[3]
        return quaternion
