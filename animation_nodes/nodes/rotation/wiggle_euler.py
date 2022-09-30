import bpy
import random
from bpy.props import *
from math import radians
from mathutils import Euler
from ... events import propertyChanged
from ... base_types import AnimationNode

class EulerWiggleNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_EulerWiggleNode"
    bl_label = "Euler Wiggle"

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
        self.newInput("Euler", "Amplitude", "amplitude", value = [radians(30), radians(30), radians(30)])
        self.newInput("Integer", "Octaves", "octaves", value = 2, minValue = 0)
        self.newInput("Float", "Persistance", "persistance", value = 0.3)

        if self.createList:
            self.newOutput("Euler List", "Eulers", "eulers")
        else:
            self.newOutput("Euler", "Euler", "euler")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row.prop(self, "createList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionCode(self, required):
        if self.createList:
            yield "_seed = seed * 23452 + self.nodeSeed * 643523"
            yield "eulers = algorithms.perlin_noise.wiggleEulerList(max(0, count), _seed + evolution * speed / 20, amplitude, octaves, persistance)"
        else:
            yield "euler = Euler(algorithms.perlin_noise.perlinNoiseVectorForNodes(seed, self.nodeSeed, evolution, speed, amplitude, octaves, persistance))"

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
