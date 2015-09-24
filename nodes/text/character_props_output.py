import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class CharacterPropertiesOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CharacterPropertiesOutputNode"
    bl_label = "Character Properties Output"

    allowNegativeIndex = BoolProperty(default = True)
    
    def create(self):
        self.inputs.new("an_ObjectSocket", "Text Object", "object").defaultDrawType = "PROPERTY_ONLY"
        
        self.inputs.new("an_IntegerSocket", "Start", "start").value = 0
        self.inputs.new("an_IntegerSocket", "End", "end").value = -1

        self.inputs.new("an_IntegerSocket", "Material Index", "materialIndex").value = 0
        self.inputs.new("an_BooleanSocket", "Bold", "bold").value = False
        self.inputs.new("an_BooleanSocket", "Italic", "italic").value = False
        self.inputs.new("an_BooleanSocket", "Underline", "underline").value = False
        self.inputs.new("an_BooleanSocket", "Small Caps", "smallCaps").value = False
        
        for socket in self.inputs[3:]:
            socket.defaultDrawType = "TEXT_ONLY"
        for socket in self.inputs[4:]:
            socket.hide = True
        self.outputs.new("an_ObjectSocket", "Object", "object")
        
    def drawAdvanced(self, layout):
        layout.prop(self, "allowNegativeIndex")
        
    def getExecutionCode(self):
        isLinked = self.getLinkedInputsDict()
        lines = []
        lines.append("if getattr(object, 'type', '') == 'FONT':")
        lines.append("    textObject = object.data")
    
        if self.allowNegativeIndex: lines.append("    s, e = start, end")
        else: lines.append("    s, e = max(0, start), max(0, end)")
    
        lines.append("    for char in textObject.body_format[s:e]:")
        if isLinked["materialIndex"]: lines.append(" "*8 + "char.material_index = materialIndex")
        if isLinked["bold"]: lines.append(" "*8 + "char.use_bold = bold")
        if isLinked["italic"]: lines.append(" "*8 + "char.use_italic = italic")
        if isLinked["underline"]: lines.append(" "*8 + "char.use_underline = underline")
        if isLinked["smallCaps"]: lines.append(" "*8 + "char.use_small_caps = smallCaps")
        lines.append("    pass")

        return lines
