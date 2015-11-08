import bpy
import random
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class RandomQuaternionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomQuaternionNode"
    bl_label = "Random Quaternion"

    nodeSeed = IntProperty(name = "Node Seed", update = propertyChanged, max = 1000, min = 0)

    def create(self):
        self.inputs.new("an_IntegerSocket", "Seed", "seed")
        self.inputs.new("an_FloatSocket", "Scale", "scale").value = 2.0
        self.outputs.new("an_QuaternionSocket", "Quaternion", "randomQuaternion")

    def draw(self, layout):
        layout.prop(self, "nodeSeed")

    def getExecutionCode(self):
        yield "startSeed = (seed + self.nodeSeed * 1000) % (len(random_number_cache) - 3)"
        yield ("randomQuaternion = mathutils.Quaternion(( 1,"
                                    "(random_number_cache[startSeed] - 0.5) * scale, "
                                    "(random_number_cache[startSeed + 1] - 0.5) * scale, "
                                    "(random_number_cache[startSeed + 2] - 0.5) * scale))")

    def getUsedModules(self):
        return ["mathutils"]

    def duplicate(self, sourceNode):
        self.nodeSeed = int(random.random() * 100)
