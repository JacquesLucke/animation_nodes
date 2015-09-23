import bpy
from ... base_types.node import AnimationNode

class ObjectVisibilityInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectVisibilityInputNode"
    bl_label = "Object Visibility Input"

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.outputs.new("an_BooleanSocket", "Hide", "hide")
        self.outputs.new("an_BooleanSocket", "Hide Select", "hideSelect").hide = True
        self.outputs.new("an_BooleanSocket", "Hide Render", "hideRender")
        self.outputs.new("an_BooleanSocket", "Show Name", "showName").hide = True
        self.outputs.new("an_BooleanSocket", "Show Axis", "showAxis").hide = True
        self.outputs.new("an_BooleanSocket", "Show Xray", "showXray").hide = True
    
    def getExecutionCode(self):

        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
        lines = []
        lines.append("if object is not None:")
        if isLinked["hide"]: lines.append("    hide = object.hide")
        if isLinked["hideSelect"]: lines.append("    hideSelect = object.hide_select")
        if isLinked["hideRender"]: lines.append("    hideRender = object.hide_render")
        if isLinked["showName"]: lines.append("    showName = object.show_name")
        if isLinked["showAxis"]: lines.append("    showAxis = object.show_axis")
        if isLinked["showXray"]: lines.append("    showXray = object.show_x_ray")
        lines.append("else: hide = hideSelect = hideRender = showName = showAxis = showXray = None")

        return lines
