import bpy, random
from bpy.types import Node
from ... mn_cache import getUniformRandom
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_RandomNumberNode(Node, AnimationNode):
    bl_idname = "mn_RandomNumberNode"
    bl_label = "Random Number"
    isDetermined = True
    
    additionalSeed = bpy.props.IntProperty(update = nodePropertyChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Seed")
        self.inputs.new("mn_FloatSocket", "Min").number = 0.0
        self.inputs.new("mn_FloatSocket", "Max").number = 1.0
        self.outputs.new("mn_FloatSocket", "Float Value")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "additionalSeed", text = "Additional Seed")
        
    def getInputSocketNames(self):
        return {"Seed" : "seed", "Min" : "minValue", "Max" : "maxValue"}
    def getOutputSocketNames(self):
        return {"Float Value" : "random_number"}
        
    def execute(self, seed, minValue, maxValue):
        return getUniformRandom(seed + 1193 * self.additionalSeed, minValue, maxValue)
        
    def copy(self, node):
        self.additionalSeed = int(random.random()*1000)
        
