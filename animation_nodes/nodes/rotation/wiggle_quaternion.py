import bpy
import random
from bpy.props import *
from mathutils import Quaternion
from ... events import propertyChanged
from ... base_types import AnimationNode

class QuaternionWiggleNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_QuaternionWiggleNode"
    bl_label = "Quaternion Wiggle"

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
        self.newInput("Quaternion", "Amplitude", "amplitude", value = [1, 0.3, 0.3, 0.3])
        self.newInput("Integer", "Octaves", "octaves", value = 2, minValue = 0)
        self.newInput("Float", "Persistance", "persistance", value = 0.3)

        if self.createList:
            self.newOutput("Quaternion List", "Quaternions", "quaternions")
        else:
            self.newOutput("Quaternion", "Quaternion", "quaternion")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row.prop(self, "createList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionCode(self, required):
        if self.createList:
            yield "_seed = seed * 23452 + self.nodeSeed * 643523"
            yield "quaternions = algorithms.perlin_noise.wiggleQuaternionList(max(0, count), _seed + evolution * speed / 20, amplitude, octaves, persistance)"
        else:
            yield "quaternion = Quaternion((1, *algorithms.perlin_noise.perlinNoiseVectorForNodes(seed, self.nodeSeed, evolution, speed, amplitude, octaves, persistance)))"

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
