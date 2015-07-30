import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... mn_utils import *

class mn_JoinTextList(Node, AnimationNode):
    bl_idname = "mn_JoinTextList"
    bl_label = "Join Text List Elements"
    #separated from Sum elements
    #adding option for negative/autoEnd like in trim - 
    #we can keep original Sum elements (hidden) for backwards compatibility

    def settingChanged(self, context):
        self.inputs["End"].hide = self.autoEnd
        nodePropertyChanged(self, context)
    
    autoEnd = bpy.props.BoolProperty(default = False, description = "Use the length of the list as trim-end", update = settingChanged)
    allowNegativeIndex =  bpy.props.BoolProperty(default = False, description = "Allow nwgative index values for start / end")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_StringListSocket", "List")
        self.inputs.new("mn_IntegerSocket", "Start").number = 0
        self.inputs.new("mn_IntegerSocket", "End").number = 5
        self.outputs.new("mn_StringSocket", "Joined Text")#or just Text?
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "autoEnd", text = "Auto End")
        layout.prop(self, "allowNegativeIndex", text = "Negative Index")
        
    def getNextNodeSuggestions(self):
        return [("mn_TextOutputNode", (0, 0)),
                ("mn_StringLengthNode", (0, 0)),
                ("mn_SplitText", (0, 0)),
                ("mn_CombineStringsNode", (0, 0))]
        
    def getInputSocketNames(self):
        return {"List" : "list",
                "Start" : "start",
                "End" : "end"}
                
    def getOutputSocketNames(self):
        return {"Joined Text" : "text"}#or just Text?
        
    def execute(self, list, start, end):
        listLength = len(list)
        
        if self.autoEnd: end = listLength
        
        minIndex = -listLength if self.allowNegativeIndex else 0
        start = min(max(minIndex, start), listLength)
        end = min(max(minIndex, end), listLength)
        
        text = "".join(list[start:end])
        
        return text
    
