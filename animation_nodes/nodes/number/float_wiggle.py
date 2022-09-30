import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class FloatWiggleNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_FloatWiggleNode"
    bl_label = "Number Wiggle"

    nodeSeed: IntProperty(update = propertyChanged)

    createList: BoolProperty(name = "Create List", default = False,
        update = AnimationNode.refresh)

    def setup(self):
        self.randomizeNodeSeed()

    def create(self):
        self.newInput("Float", "Seed", "seed")
        if self.createList:
            self.newInput("Integer", "Count", "count", value = 5, minValue = 0)
        self.newInput("Float", "Evolution", "evolution")
        self.newInput("Float", "Speed", "speed", value = 1, minValue = 0)
        self.newInput("Float", "Amplitude", "amplitude", value = 1.0)
        self.newInput("Integer", "Octaves", "octaves", value = 2, minValue = 0)
        self.newInput("Float", "Persistance", "persistance", value = 0.3)

        if self.createList:
            self.newOutput("Float List", "Numbers", "numbers")
        else:
            self.newOutput("Float", "Number", "number")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row.prop(self, "createList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionCode(self, required):
        if self.createList:
            yield "_seed = seed * 23452 + self.nodeSeed * 643523"
            yield "numbers = algorithms.perlin_noise.wiggleDoubleList(max(0, count), _seed + evolution * speed / 20, amplitude, octaves, persistance)"
        else:
            yield "number = algorithms.perlin_noise.perlinNoiseForNodes(seed, self.nodeSeed, evolution, speed, amplitude, octaves, persistance)"

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
