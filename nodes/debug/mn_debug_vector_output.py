import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_DebugVectorOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_DebugVectorOutputNode"
    bl_label = "Debug Vector Output"
    
    debugOutputString_component0 = bpy.props.StringProperty(default = "")
    debugOutputString_component1 = bpy.props.StringProperty(default = "")
    debugOutputString_component2 = bpy.props.StringProperty(default = "")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "Vector")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.label(self.debugOutputString_component0)
        layout.label(self.debugOutputString_component1)
        layout.label(self.debugOutputString_component2)
        
    def execute(self, input):
        self.debugOutputString_component0 = "X: "+str(round(input["Vector"][0], 2))
        self.debugOutputString_component1 = "Y: "+str(round(input["Vector"][1], 2))
        self.debugOutputString_component2 = "Z: "+str(round(input["Vector"][2], 2))
        return {}

