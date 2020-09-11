import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... utils.math import cantorPair
from ... base_types import AnimationNode
from . c_utils import generateRandomBooleans
from ... algorithms.random import uniformRandomDoubleWithTwoSeeds

class RandomBooleanNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomBooleanNode"
    bl_label = "Random Boolean"

    nodeSeed: IntProperty(update = propertyChanged, min = 0)

    createList: BoolProperty(name = "Create List", default = False,
        description = "Create a list of random booleans",
        update = AnimationNode.refresh)

    def create(self):
        if self.createList:
            self.newInput("Integer", "Seed", "seed")
            self.newInput("Integer", "Count", "count", value = 5, minValue = 1)
            self.newOutput("Boolean List", "Booleans", "booleans")
        else:
            self.newInput("Integer", "Seed", "seed")
            self.newOutput("Boolean", "Boolean", "boolean")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row.prop(self, "createList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionCode(self, required):
        if self.createList:
            yield "booleans = self.execute_list(seed, count)"
        else:
            yield "boolean = self.execute_single(seed)"

    def execute_list(self, seed, count):
        seed_ = cantorPair(max(seed, 0), self.nodeSeed)

        return generateRandomBooleans(count, seed_)

    def execute_single(self, seed):
        seed_ = cantorPair(max(seed, 0), self.nodeSeed)
        random.seed(seed_)
        intnum = random.randint(0,1)

        return bool(intnum)

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
