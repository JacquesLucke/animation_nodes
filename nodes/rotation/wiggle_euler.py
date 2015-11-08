import bpy
from bpy.props import *
from mathutils import Euler
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.perlin_noise import perlinNoise

class EulerWiggleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EulerWiggleNode"
    bl_label = "Euler Wiggle"

    nodeSeed = IntProperty(update = propertyChanged)

    def create(self):
        self.inputs.new("an_FloatSocket", "Seed", "seed")
        self.inputs.new("an_FloatSocket", "Evolution", "evolution")
        self.inputs.new("an_EulerSocket", "Amplitude", "amplitude").value = [1.570796, 1.570796, 1.570796]
        self.inputs.new("an_IntegerSocket", "Octaves", "octaves").value = 2
        self.inputs.new("an_FloatSocket", "Persistance", "persistance").value = 0.3
        self.outputs.new("an_EulerSocket", "Euler", "euler")

    def draw(self, layout):
        layout.prop(self, "nodeSeed", text = "Node Seed")

    def execute(self, seed, evolution, amplitude, octaves, persistance):
        euler = Euler()
        evolution = evolution + 2541 * seed + 823 * self.nodeSeed
        euler[0] = perlinNoise(evolution, persistance, octaves) * amplitude[0]
        evolution += 79
        euler[1] = perlinNoise(evolution, persistance, octaves) * amplitude[1]
        evolution += 263
        euler[2] = perlinNoise(evolution, persistance, octaves) * amplitude[2]
        return euler
