import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

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
        self.newInput("Float", "Probability", "probability", value = 0.5, minValue = 0, maxValue = 1, hide = True)

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row.prop(self, "createList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionCode(self, required):
        yield "_seed = AN.utils.math.cantorPair(max(seed, 0), self.nodeSeed)"
        if self.createList:
            yield "booleans = AN.nodes.boolean.c_utils.generateRandomBooleans(_seed, count, probability)"
        else:
            yield "boolean = self.execute_single(_seed, probability)"

    def execute_single(self, seed, probability):
        random.seed(seed)  
        return random.random() < probability

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
