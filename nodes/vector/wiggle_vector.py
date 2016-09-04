import bpy
import random
from bpy.props import *
from mathutils import Vector
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... algorithms.perlin_noise import perlinNoise

class VectorWiggleNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_VectorWiggleNode"
    bl_label = "Vector Wiggle"

    nodeSeed = IntProperty(update = propertyChanged)

    def create(self):
        self.newInput("Float", "Seed", "seed")
        self.newInput("Float", "Evolution", "evolution")
        self.newInput("Float", "Speed", "speed", value = 1, minValue = 0)
        self.newInput("Vector", "Amplitude", "amplitude", value = [5, 5, 5])
        self.newInput("Integer", "Octaves", "octaves", value = 2)
        self.newInput("Float", "Persistance", "persistance", value = 0.3)
        self.newOutput("Vector", "Vector", "vector")
        self.randomizeNodeSeed()

    def draw(self, layout):
        layout.prop(self, "nodeSeed", text = "Node Seed")

    def getExecutionCode(self):
        yield "vector = Vector(algorithms.perlin_noise.perlinNoiseVectorForNodes(seed, self.nodeSeed, evolution, speed, amplitude, octaves, persistance))"

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
