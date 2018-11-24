import bpy
from ... base_types import AnimationNode, VectorizedSocket

class ObjectVisibilityInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectVisibilityInputNode"
    bl_label = "Object Visibility Input"
    codeEffects = [VectorizedSocket.CodeEffect]

    useObjectList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput(VectorizedSocket("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects"),
            codeProperties = dict(allowListExtension = False)))

        self.newOutput(VectorizedSocket("Boolean", "useObjectList",
            ("Hide Viewport", "hideViewport"), ("Hide Viewport", "hideViewport")))
        self.newOutput(VectorizedSocket("Boolean", "useObjectList",
            ("Hide Render", "hideRender"), ("Hide Render", "hideRender")))
        self.newOutput(VectorizedSocket("Boolean", "useObjectList",
            ("Hide Select", "hideSelect"), ("Hide Select", "hideSelect")))
        self.newOutput(VectorizedSocket("Boolean", "useObjectList",
            ("Show Name", "showName"), ("Show Name", "showName")))
        self.newOutput(VectorizedSocket("Boolean", "useObjectList",
            ("Show Axis", "showAxis"), ("Show Axis", "showAxis")))
        self.newOutput(VectorizedSocket("Boolean", "useObjectList",
            ("Show In Front", "showInFront"), ("Show In Front", "showInFront")))

        for socket in self.outputs[2:]:
            socket.hide = True

    def getExecutionCode(self, required):
        if len(required) == 0:
            return

        yield "if object is not None:"
        if "hideViewport" in required:        yield "    hideViewport = object.hide_viewport"
        if "hideSelect" in required:  yield "    hideSelect = object.hide_select"
        if "hideRender" in required:  yield "    hideRender = object.hide_render"
        if "showName" in required:    yield "    showName = object.show_name"
        if "showAxis" in required:    yield "    showAxis = object.show_axis"
        if "showInFront" in required:    yield "    showInFront = object.show_in_front"

        yield "else:"
        yield "    hideViewport = hideSelect = hideRender = showName = showAxis = showInFront = False"
