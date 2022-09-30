import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode

class RandomQuaternionNode(AnimationNode, bpy.types.Node):
    bl_idname = "an_RandomQuaternionNode"
    bl_label = "Random Quaternion"

    nodeSeed: IntProperty(name = "Node Seed", update = propertyChanged, max = 1000, min = 0)

    createList: BoolProperty(name = "Create List", default = False,
        description = "Create a list of random quaternions",
        update = AnimationNode.refresh)

    def create(self):
        if self.createList:
            self.newInput("Integer", "Seed", "seed")
            self.newInput("Integer", "Count", "count", value = 5, minValue = 0)
            self.newOutput("Quaternion List", "Quaternions", "randomQuaternions")
        else:
            self.newInput("Integer", "Seed", "seed")
            self.newOutput("Quaternion", "Quaternion", "randomQuaternion")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row.prop(self, "createList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionCode(self, required):
        yield "_seed = AN.utils.math.cantorPair(max(seed, 0), self.nodeSeed)"
        if self.createList:
            yield "randomQuaternions = AN.nodes.rotation.c_utils.randomQuaternionList(_seed, count)"
        else:
            yield "randomQuaternion = Quaternion(algorithms.random.randomNumberTuple(_seed, 4, math.pi))"
            yield "randomQuaternion.normalize()"

    def getUsedModules(self):
        return ["math"]

    def duplicate(self, sourceNode):
        self.nodeSeed = int(random.random() * 100)
        
    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
