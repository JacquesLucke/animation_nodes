import bpy, re
from ... mn_node_base import AnimationNode
from ... mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
from ... mn_utils import *

splitTypes = [
    ("Characters", "Characters", ""),
    ("Words", "Words", ""),
    ("Lines", "Lines", ""),
    ("Regexp", "Regexp", "") ]

class mn_SplitText(bpy.types.Node, AnimationNode):
    bl_idname = "mn_SplitText"
    bl_label = "Split Text"
    
    def splitTypeChanges(self, context):
        self.setHideProperty()
    
    splitType = bpy.props.EnumProperty(name = "Split Type", default = "Regexp", items = splitTypes, update = splitTypeChanges)
    keepDelimiters = bpy.props.BoolProperty(default = False)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_StringSocket", "Text")
        self.inputs.new("mn_StringSocket", "Split By")
        self.outputs.new("mn_StringListSocket", "Text List")
        self.outputs.new("mn_IntegerSocket", "Length")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "splitType", text = "Type")
        if self.splitType == "Regexp": layout.prop(self, "keepDelimiters", text = "Keep Delimiters")
        
    def setHideProperty(self):
        self.inputs["Split By"].hide = not self.splitType == "Regexp"

        
    def getInputSocketNames(self):
        return {"Text" : "text",
                "Split By" : "splitBy"}
    def getOutputSocketNames(self):
        return {"Text List" : "textList",
                "Length" : "length"}

    def execute(self, text, splitBy):
        textList = []

        if self.splitType == "Characters": textList = list(text)
        elif self.splitType == "Words": textList = text.split()
        elif self.splitType == "Lines": textList = text.split("\n")

        elif self.splitType == "Regexp":
            if splitBy == "": textList = [text]
            else:
                if self.keepDelimiters: textList = re.split("("+splitBy+")", text)
                else: textList = re.split(splitBy, text)

        return textList, len(textList)
