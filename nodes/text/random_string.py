import bpy
import random
from ... base_types.node import AnimationNode

class RandomStringNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_RandomStringNode"
    bl_label = "Random Text"

    inputNames = { "Seed" : "seed",
                   "Length" : "length",
                   "Characters" : "characters" }

    outputNames = { "Text" : "text" }

    def create(self):
        self.inputs.new("mn_IntegerSocket", "Seed")
        self.inputs.new("mn_IntegerSocket", "Length").value = 5
        self.inputs.new("mn_StringSocket", "Characters").value = "abcdefghijklmnopqrstuvwxyz"
        self.outputs.new("mn_StringSocket", "Text")

    def execute(self, seed, length, characters):
        random.seed(seed)
        return ''.join(random.choice(characters) for _ in range(length))
