import bpy
from ... mn_cache import getUniformRandom
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged

class RandomNumberNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_RandomNumberNode"
    bl_label = "Random Number"
    isDetermined = True
    
    additionalSeed = bpy.props.IntProperty(update = nodePropertyChanged)
    
    def create(self):
        self.inputs.new("mn_IntegerSocket", "Seed")
        self.inputs.new("mn_FloatSocket", "Min").number = 0.0
        self.inputs.new("mn_FloatSocket", "Max").number = 1.0
        self.outputs.new("mn_FloatSocket", "Number")
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "additionalSeed", text = "Additional Seed")
        
    def getInputSocketNames(self):
        return {"Seed" : "seed", 
                "Min" : "minValue", 
                "Max" : "maxValue"}
                
    def getOutputSocketNames(self):
        return {"Number" : "number"}
        
    def execute(self, seed, minValue, maxValue):
        return getUniformRandom(seed + 1193 * self.additionalSeed, minValue, maxValue)
        
    def copy(self, node):
        self.additionalSeed = int(random.random()*1000)
        
