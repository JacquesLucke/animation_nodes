import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

compare_types = ["A = B", "A != B", "A < B", "A <= B", "A > B", "A >= B", "A is B"]
compare_types_items = [(t, t, "") for t in compare_types]

class mn_CompareNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CompareNode"
    bl_label = "Compare"
    
    compareType = bpy.props.EnumProperty(name = "Compare Type", items = compare_types_items, update = nodeTreeChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_GenericSocket", "A")
        self.inputs.new("mn_GenericSocket", "B")
        self.outputs.new("mn_BooleanSocket", "Result")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"A" : "a",
                "B" : "b"}
    def getOutputSocketNames(self):
        return {"Result" : "result"}
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "compareType", text = "Type")
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        type = self.compareType
        if type == "A = B":	return "$result$ = %a% == %b%"
        if type == "A != B":	return "$result$ = %a% != %b%"
        if type == "A < B":	return "try: $result$ = %a% < %b% \nexcept: $result$ = False"
        if type == "A <= B":	return "try: $result$ = %a% <= %b% \nexcept: $result$ = False"
        if type == "A > B":	return "try: $result$ = %a% > %b% \nexcept: $result$ = False"
        if type == "A >= B":	return "try: $result$ = %a% >= %b% \nexcept: $result$ = False"
        if type == "A is B":	return "$result$ = %a% is %b%"
        return "$result$ = False"
