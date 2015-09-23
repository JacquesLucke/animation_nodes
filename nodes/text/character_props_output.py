import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class CharacterPropsOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CharacterPropsOutputNode"
    bl_label = "Character Props Output"
    
    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        executionCodeChanged()
    
    materialIndex = BoolProperty(default = True, description ="Set Material Index", update = checkedPropertiesChanged)
    
    useBold = BoolProperty(default = False, description ="Use Bold", update = checkedPropertiesChanged)
    useItalic = BoolProperty(default = False, description ="Use Italic", update = checkedPropertiesChanged)
    useUnderline = BoolProperty(default = False, description ="Underline", update = checkedPropertiesChanged)
    useSmallCaps = BoolProperty(default = False, description ="Small Caps", update = checkedPropertiesChanged)
    
    allowNegativeIndex = BoolProperty(default = True)
    
    def create(self):
        self.inputs.new("an_ObjectSocket", "Text Object", "object").defaultDrawType = "PROPERTY_ONLY"
        
        self.inputs.new("an_IntegerSocket", "Start", "start").value = 0
        self.inputs.new("an_IntegerSocket", "End", "end").value = -1

        self.inputs.new("an_IntegerSocket", "Material Index", "materialIndex").value = 0
        self.inputs.new("an_BooleanSocket", "Bold", "bold").value = False
        self.inputs.new("an_BooleanSocket", "Italic", "italic").value = False
        
        self.inputs.new("an_BooleanSocket", "Underline", "underline").value = False
        self.inputs.new("an_FloatSocket", "Underline Position", "underlinePosition").value = 0.0
        self.inputs.new("an_FloatSocket", "Underline Thickness", "underlineThickness").value = 0.05
        
        self.inputs.new("an_BooleanSocket", "Small Caps", "smallCaps").value = False
        self.inputs.new("an_FloatSocket", "Small Caps Scale", "smallCapsScale").value = 0.75
        self.updateSocketVisibility()
        
        self.outputs.new("an_ObjectSocket", "Object", "object")
        
    def draw(self, layout):
        col = layout.column(align = True)
        row = col.row(align = True)
        row.prop(self, "materialIndex", text = "", icon = "MATERIAL_DATA")  #MATSPHERE
        row.separator()
        row.prop(self, "useBold", text = "", icon = "FONT_DATA")
        row.prop(self, "useItalic", text = "", icon = "OUTLINER_DATA_FONT")
        row.prop(self, "useUnderline", text = "", icon = "FONTPREVIEW")
        row.prop(self, "useSmallCaps", text = "", icon = "SYNTAX_OFF")   #FILE_FONT

    def drawAdvanced(self, layout):
        layout.prop(self, "show_options")
        layout.prop(self, "allowNegativeIndex")
        
    def updateSocketVisibility(self):
        self.inputs["Material Index"].hide = not (self.materialIndex)
        self.inputs["Bold"].hide = not (self.useBold)
        self.inputs["Italic"].hide = not (self.useItalic)
            
        self.inputs["Underline"].hide = not (self.useUnderline)
        self.inputs["Underline Position"].hide = not (self.useUnderline)
        self.inputs["Underline Thickness"].hide = not (self.useUnderline)
            
        self.inputs["Small Caps"].hide = not (self.useSmallCaps)
        self.inputs["Small Caps Scale"].hide = not (self.useSmallCaps)
            
    def getExecutionCode(self):
        lines = []
        if not any([self.materialIndex, self.useBold, self.useItalic, self.useUnderline, self.useSmallCaps]):
            lines = []
        else:
            lines.append("if getattr(object, 'type', '') == 'FONT':")
            lines.append("    textObject = object.data")
        
            if self.allowNegativeIndex: lines.append("    s, e = start, end")
            else: lines.append("    s, e = max(0, start), max(0, end)")
        
            lines.append("    for char in textObject.body_format[s:e]:")
            if self.materialIndex: lines.append(" "*8 + "char.material_index = materialIndex")
            if self.useBold: lines.append(" "*8 + "char.use_bold = bold")
            if self.useItalic: lines.append(" "*8 + "char.use_italic = italic")
            if self.useUnderline: lines.append(" "*8 + "char.use_underline = underline")
            if self.useSmallCaps: 
                lines.append(" "*8 + "char.use_small_caps = smallCaps")
                lines.append("    textObject.small_caps_scale = smallCapsScale")
            if self.useUnderline: 
                lines.append("    textObject.underline_position = underlinePosition")
                lines.append("    textObject.underline_height = underlineThickness")

        return lines
