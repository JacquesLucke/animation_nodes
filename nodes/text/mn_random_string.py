import bpy, random
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_RandomStringNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_RandomStringNode"
    bl_label = "Random Text"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Seed")
        self.inputs.new("mn_IntegerSocket", "Length").number = 5
        self.inputs.new("mn_StringSocket", "Characters").string = "abcdefghijklmnopqrstuvwxyz"
        self.outputs.new("mn_StringSocket", "Text")
        allowCompiling()
        
    def execute(self, input):
        output = {}
        seed = input["Seed"]
        length = input["Length"]
        characters = input["Characters"]
        random.seed(seed)
        output["Text"] = ''.join(random.choice(characters) for _ in range(length))
        return output
