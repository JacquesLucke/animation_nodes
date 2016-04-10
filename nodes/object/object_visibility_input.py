import bpy
from ... base_types.node import AnimationNode

class ObjectVisibilityInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectVisibilityInputNode"
    bl_label = "Object Visibility Input"

    def create(self):
        self.newInput("an_ObjectSocket", "Object", "object").defaultDrawType = "PROPERTY_ONLY"
        self.newOutput("an_BooleanSocket", "Hide", "hide")
        self.newOutput("an_BooleanSocket", "Hide Select", "hideSelect").hide = True
        self.newOutput("an_BooleanSocket", "Hide Render", "hideRender")
        self.newOutput("an_BooleanSocket", "Show Name", "showName").hide = True
        self.newOutput("an_BooleanSocket", "Show Axis", "showAxis").hide = True
        self.newOutput("an_BooleanSocket", "Show Xray", "showXray").hide = True

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

        yield "if object is not None:"

        if isLinked["hide"]:        yield "    hide = object.hide"
        if isLinked["hideSelect"]:  yield "    hideSelect = object.hide_select"
        if isLinked["hideRender"]:  yield "    hideRender = object.hide_render"
        if isLinked["showName"]:    yield "    showName = object.show_name"
        if isLinked["showAxis"]:    yield "    showAxis = object.show_axis"
        if isLinked["showXray"]:    yield "    showXray = object.show_x_ray"

        yield "else: hide = hideSelect = hideRender = showName = showAxis = showXray = None"
