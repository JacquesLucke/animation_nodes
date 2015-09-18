import bpy
from bpy.props import BoolProperty
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class an_ObjectVisibilityOutput(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectVisibilityOutput"
    bl_label = "Object Visibility Output"
    
    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        executionCodeChanged()
    
    #these are common obj props, the rest are type dependent
    useView = BoolProperty(name = "Use Hide", default = False, description = "Set Hide (restrict viewport visibility)", update = checkedPropertiesChanged)
    useSelect = BoolProperty(name = "Use Hide Select", default = False, description = "Set Hide Select (restrict viewport selection)", update = checkedPropertiesChanged)
    useRender = BoolProperty(name = "Use Hide Render", default = False, description = "Set Hide Render (restrict rendering)", update = checkedPropertiesChanged)

    useName = BoolProperty(name = "Use Name", default = False, description = "Set Show Name (visibility for object name)", update = checkedPropertiesChanged)
    useAxis = BoolProperty(name = "Use Axis", default = False, description = "Set Show Axis (visibility for object origin and axes)", update = checkedPropertiesChanged)
    useXray = BoolProperty(name = "Use Xray", default = False, description = "Set Show X-Ray (visibility for the object in front of others)", update = checkedPropertiesChanged)

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_BooleanSocket", "Hide", "hide").value = False
        self.inputs.new("an_BooleanSocket", "Hide Select", "hideSelect").value = False
        self.inputs.new("an_BooleanSocket", "Hide Render", "hideRender").value = False
        self.inputs.new("an_BooleanSocket", "Show Name", "showName").value = False
        self.inputs.new("an_BooleanSocket", "Show Axis", "showAxis").value = False
        self.inputs.new("an_BooleanSocket", "Show Xray", "showXray").value = False
        self.outputs.new("an_ObjectSocket", "Object", "object")
        self.updateSocketVisibility()
        
    def draw(self, layout):
        rrow = layout.row()
        
        col = rrow.column()
        row = col.row(align = True)
        row.alignment = 'LEFT'
        #row.label("Visibility")
        row.prop(self, "useView", text = "", icon = "RESTRICT_VIEW_OFF")
        row.prop(self, "useSelect", text = "", icon = "RESTRICT_SELECT_OFF")
        row.prop(self, "useRender", text = "", icon = "RESTRICT_RENDER_OFF")
        
        col = rrow.column()
        row = col.row(align = True)
        row.alignment = 'RIGHT'
        #row.label("Show")
        row.prop(self, "useName", text = "", icon = "SORTALPHA")    # SYNTAX_ON / SYNTAX_OFF
        row.prop(self, "useAxis", text = "", icon = "MANIPUL")    
        row.prop(self, "useXray", text = "", icon = "ROTACTIVE")    # MOD_DECIM / META_BALL
    
    def drawAdvanced(self, layout):
        layout.operator("wm.call_menu", text = "Node Info / Help", icon = "INFO").name = "an.show_obj_vis_help"

    def updateSocketVisibility(self):
        self.inputs["Hide"].hide = not (self.useView)
        self.inputs["Hide Select"].hide = not (self.useSelect)
        self.inputs["Hide Render"].hide = not (self.useRender)
        self.inputs["Show Name"].hide = not (self.useName)
        self.inputs["Show Axis"].hide = not (self.useAxis)
        self.inputs["Show Xray"].hide = not (self.useXray)
        
    def getExecutionCode(self):
        lines = []
        lines.append("if object is not None:")
        
        if self.useView: lines.append("    object.hide = hide")
        if self.useSelect: lines.append("    object.hide_select = hideSelect")
        if self.useRender: lines.append("    object.hide_render = hideRender")
        
        if self.useName: lines.append("    object.show_name = showName")
        if self.useAxis: lines.append("    object.show_axis = showAxis")
        if self.useXray: lines.append("    object.show_x_ray = showXray")
        
        if not any((self.useView, self.useSelect, self.useRender, self.useName, self.useAxis, self.useXray)): 
            lines = []
            
        #lines.append("object = object")
        return lines


class ShowHelp(bpy.types.Menu):
    bl_idname = "an.show_obj_vis_help"
    bl_label = "Object Visibility Output node | Blender - Animation Nodes"
    bl_icon = "FORCE_TURBULENCE"
    
    helpText = bpy.props.StringProperty(default = "help here")
    noteText = bpy.props.StringProperty(default = "note here")
    helpLines = []
    noteLines = []
    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.label('''Help, comments, notes.''', icon = "INFO")
        row = layout.row(align = True)
        
        col = row.column(align = True)
        helpLines = self.helpText.split("\n")
        for li in helpLines:
            if li:
                col.label(text=li)
                
        col = row.column(align = True)
        noteLines = self.noteText.split("\n")
        for li in noteLines:
            if li:
                col.label(text=li)
            
        layout.label("o.g. 08.2015", icon = "INFO")
        
    helpText ='''
Purpose:
    This is a convenience node made to ease some ui procedures.
    Especially useful for objects generated by AN, when many.
    
    Allows hiding in the view or render, showing the names etc. ,
    the commands usually found in Outliner and Object properties panels
    Having as nodes is especially useful for many instanced objects, 
    or for hiding source of meshes.
    
Usage:
    Connect after the object you want to change state. Connect in loops
    for changing many at once. 
    Check the upper buttons for the parameters you want to affect.
    The props unchecked will not be affected in the object. This 
    is important for use in loops, where affecting many objects. 
    
    The top row of buttons correspond to the order of sockets:
    [hide][hide select][hide render]    [show name][show axis][show Xray]
       hide = hide in viewport
       hide select = hide from selection
       hide render = hide from rendering
       show name = shows name of the object in the viewport
       show axis = show origin and xyz tripod of the object
       show Xray = shows the object in front of others, never hidden
'''
    noteText ='''
notes:
    By default, parameters are Not checked. 
    Normally it all are Unchecked so that nothing is changed by accident.
    Also, the default values are False. This being more serious.
    
    To change these go into the [an_object_visibility_output.py] file 
    (normally in animation nodes / nodes / object folder) and
    by the lines 14 to 20 you'll find the default states of these buttons.
    Change to True instead of False those that you consider by default
    
    You should not change the default values, near the sockets, 
    as they can lead to unwanted, blind, hiding the moment you plug 
    an object 
    
To explore further:
    there is also an Object Visibility Input brother node.
    That reads the state from objects.
    
    I think is less used, but it' there for convenience.
    Normally it is not in menu, so use search (Shift A)
'''