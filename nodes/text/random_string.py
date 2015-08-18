import bpy
import random
from ... base_types.node import AnimationNode

class RandomStringNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomStringNode"
    bl_label = "Random Text"

    def create(self):
        self.inputs.new("an_IntegerSocket", "Seed", "seed")
        self.inputs.new("an_IntegerSocket", "Length", "length").value = 5
        self.inputs.new("an_StringSocket", "Characters", "characters").value = "abcdefghijklmnopqrstuvwxyz"
        self.outputs.new("an_StringSocket", "Text", "text")

    def execute(self, seed, length, characters):
        random.seed(seed)
        return ''.join(random.choice(characters) for _ in range(length))
