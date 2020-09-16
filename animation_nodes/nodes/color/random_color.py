import bpy
import random
from bpy.props import *
from ... data_structures import Color
from ... events import propertyChanged
from ... base_types import AnimationNode
from . c_utils import generateRandomColors

class RandomColor(bpy.types.Node, AnimationNode):
    bl_idname = "an_RandomColor"
    bl_label = "Random Color"

    nodeSeed: IntProperty(name = "Node Seed", update = propertyChanged, min = 0)

    createList: BoolProperty(name = "Create List", default = False,
        description = "Create a list of random colors",
        update = AnimationNode.refresh)

    def setup(self):
        self.randomizeNodeSeed()    

    def create(self):
        if self.createList:
            self.newInput("Integer", "Count", "count", value = 5, minValue = 0)
            self.newInput("Integer", "Seed", "seed")
            self.newOutput("Color List", "Colors", "colors")
        else:
            self.newInput("Integer", "Seed", "seed")
            self.newOutput("Color", "Color", "color")  

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "nodeSeed", text = "Node Seed")
        row.prop(self, "createList", text = "", icon = "LINENUMBERS_ON") 

    def getExecutionCode(self, required):
        yield "seed_ = AN.utils.math.cantorPair(max(seed, 0), self.nodeSeed)"
        if self.createList:
            yield "colors = self.execute_colorList(count, seed_)"
        else:
            yield "color = self.execute_colorSingle(seed_)"

    def execute_colorList(self, count, seed):
        return generateRandomColors(count, seed)

    def execute_colorSingle(self, seed):
        random.seed(seed)
        r = random.random()
        g = random.random()
        b = random.random()

        return Color((r, g, b, 1.0))

    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)       
        
