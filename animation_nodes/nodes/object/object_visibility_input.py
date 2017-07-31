import bpy
from ... base_types import VectorizedNode

class ObjectVisibilityInputNode(bpy.types.Node, VectorizedNode):
    bl_idname = "an_ObjectVisibilityInputNode"
    bl_label = "Object Visibility Input"
    autoVectorizeExecution = True

    useObjectList = VectorizedNode.newVectorizeProperty()

    def create(self):
        self.newVectorizedInput("Object", "useObjectList",
            ("Object", "object", dict(defaultDrawType = "PROPERTY_ONLY")),
            ("Objects", "objects"))

        self.newVectorizedOutput("Boolean", "useObjectList",
            ("Hide", "hide"), ("Hide", "hide"))
        self.newVectorizedOutput("Boolean", "useObjectList",
            ("Hide Render", "hideRender"), ("Hide Render", "hideRender"))
        self.newVectorizedOutput("Boolean", "useObjectList",
            ("Hide Select", "hideSelect"), ("Hide Select", "hideSelect"))
        self.newVectorizedOutput("Boolean", "useObjectList",
            ("Show Name", "showName"), ("Show Name", "showName"))
        self.newVectorizedOutput("Boolean", "useObjectList",
            ("Show Axis", "showAxis"), ("Show Axis", "showAxis"))
        self.newVectorizedOutput("Boolean", "useObjectList",
            ("Show Xray", "showXray"), ("Show Xray", "showXray"))

        for socket in self.outputs[2:]:
            socket.hide = True

    def getExecutionCode(self, required):
        if len(required) == 0:
            return

        yield "if object is not None:"
        if "hide" in required:        yield "    hide = object.hide"
        if "hideSelect" in required:  yield "    hideSelect = object.hide_select"
        if "hideRender" in required:  yield "    hideRender = object.hide_render"
        if "showName" in required:    yield "    showName = object.show_name"
        if "showAxis" in required:    yield "    showAxis = object.show_axis"
        if "showXray" in required:    yield "    showXray = object.show_x_ray"

        yield "else:"
        yield "    hide = hideSelect = hideRender = showName = showAxis = showXray = False"
