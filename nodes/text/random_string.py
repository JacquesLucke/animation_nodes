import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class RandomStringNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomStringNode"
    bl_label = "Random Text"

    nodeSeed = IntProperty(name = "Node Seed", update = propertyChanged)

    def create(self):
        self.newInput("Integer", "Seed", "seed")
        self.newInput("Integer", "Length", "length", value = 5)
        self.newInput("String", "Characters", "characters", value = "abcdefghijklmnopqrstuvwxyz")
        self.newOutput("String", "Text", "text")
        self.randomizeNodeSeed()

    def draw(self, layout):
        layout.prop(self, "nodeSeed")

    def execute(self, seed, length, characters):
        random.seed(seed + 12334 * self.nodeSeed)
        return ''.join(random.choice(characters) for _ in range(length))

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
