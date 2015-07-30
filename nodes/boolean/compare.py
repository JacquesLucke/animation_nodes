import bpy
from ... base_types.node import AnimationNode
from ... events import executionCodeChanged

compare_types = ["A = B", "A != B", "A < B", "A <= B", "A > B", "A >= B", "A is B"]
compare_types_items = [(t, t, "") for t in compare_types]

class CompareNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CompareNode"
    bl_label = "Compare"
    
    inputNames = { "A" : "a",
                   "B" : "b" }
    outputNames = { "Result" : "result" }                 
    
    compareType = bpy.props.EnumProperty(name = "Compare Type", items = compare_types_items, update = executionCodeChanged)
    
    def create(self):
        self.inputs.new("mn_GenericSocket", "A")
        self.inputs.new("mn_GenericSocket", "B")
        self.outputs.new("mn_BooleanSocket", "Result")
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "compareType", text = "Type")
        
    def getExecutionCode(self, outputUse):
        type = self.compareType
        if type == "A = B":	return "$result$ = %a% == %b%"
        if type == "A != B": return "$result$ = %a% != %b%"
        if type == "A < B":	return "try: $result$ = %a% < %b% \nexcept: $result$ = False"
        if type == "A <= B": return "try: $result$ = %a% <= %b% \nexcept: $result$ = False"
        if type == "A > B":	return "try: $result$ = %a% > %b% \nexcept: $result$ = False"
        if type == "A >= B": return "try: $result$ = %a% >= %b% \nexcept: $result$ = False"
        if type == "A is B": return "$result$ = %a% is %b%"
        return "$result$ = False"