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
        self.inputs.new("an_FloatSocket", "Seed", "seed")
        self.inputs.new("an_FloatSocket", "Evolution", "evolution")
        self.inputs.new("an_QuaternionSocket", "Amplitude", "amplitude").value = [1, 0.5, 0.5, 0.5]
        self.inputs.new("an_IntegerSocket", "Octaves", "octaves").value = 2
        self.inputs.new("an_FloatSocket", "Persistance", "persistance").value = 0.3
        self.outputs.new("an_QuaternionSocket", "Quaternion", "quaternion")

    def draw(self, layout):
        layout.prop(self, "nodeSeed", text = "Node Seed")

    def execute(self, seed, evolution, amplitude, octaves, persistance):
        quaternion = Quaternion()
        quaternion[0] = amplitude[0]
        evolution = evolution + 2541 * seed + 823 * self.nodeSeed
        quaternion[1] = perlinNoise(evolution, persistance, octaves) * amplitude[1]
        evolution += 79
        quaternion[2] = perlinNoise(evolution, persistance, octaves) * amplitude[2]
        evolution += 263
        quaternion[3] = perlinNoise(evolution, persistance, octaves) * amplitude[3]
        return quaternion
