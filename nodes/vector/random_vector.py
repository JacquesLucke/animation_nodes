import bpy
import random
from bpy.props import *
from mathutils import Vector
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class RandomVectorNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomVectorNode"
    bl_label = "Random Vector"

    nodeSeed = IntProperty(name = "Node Seed", update = propertyChanged, max = 1000, min = 0)

    def create(self):
        self.inputs.new("an_IntegerSocket", "Seed", "seed")
        self.inputs.new("an_FloatSocket", "Scale", "scale").value = 2.0
        self.outputs.new("an_VectorSocket", "Vector", "randomVector")

    def draw(self, layout):
        layout.prop(self, "nodeSeed")

    def getExecutionCode(self):
        yield "startSeed = (seed + self.nodeSeed * 1000) % (len(random_number_cache) - 3)"
        yield ("randomVector = scale * mathutils.Vector((random_number_cache[startSeed] - 0.5, "
                                                         "random_number_cache[startSeed + 1] - 0.5, "
                                                         "random_number_cache[startSeed + 2] - 0.5))")

    def getUsedModules(self):
        return ["mathutils"]

    def duplicate(self, sourceNode):
        self.nodeSeed = int(random.random() * 100)
