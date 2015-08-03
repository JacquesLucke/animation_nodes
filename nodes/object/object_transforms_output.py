import bpy
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class an_ObjectTransformsOutput(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectTransformsOutput"
    bl_label = "Transforms Output"

    inputNames = { "Object" : "object",
                   "Location" : "location",
                   "Rotation" : "rotation",
                   "Scale" : "scale" }

    outputNames = { "Object" : "object" }

    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        executionCodeChanged()

    useLocation = bpy.props.BoolVectorProperty(update = checkedPropertiesChanged)
    useRotation = bpy.props.BoolVectorProperty(update = checkedPropertiesChanged)
    useScale = bpy.props.BoolVectorProperty(update = checkedPropertiesChanged)

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object").showName = False
        self.inputs.new("an_VectorSocket", "Location")
        self.inputs.new("an_VectorSocket", "Rotation")
        self.inputs.new("an_VectorSocket", "Scale").value = (1, 1, 1)
        self.outputs.new("an_ObjectSocket", "Object")
        self.updateSocketVisibility()

    def draw_buttons(self, context, layout):
        col = layout.column(align = True)

        row = col.row(align = True)
        row.label("Location")
        row.prop(self, "useLocation", index = 0, text = "X")
        row.prop(self, "useLocation", index = 1, text = "Y")
        row.prop(self, "useLocation", index = 2, text = "Z")
        row = col.row(align = True)
        row.label("Rotation")
        row.prop(self, "useRotation", index = 0, text = "X")
        row.prop(self, "useRotation", index = 1, text = "Y")
        row.prop(self, "useRotation", index = 2, text = "Z")
        row = col.row(align = True)
        row.label("Scale")
        row.prop(self, "useScale", index = 0, text = "X")
        row.prop(self, "useScale", index = 1, text = "Y")
        row.prop(self, "useScale", index = 2, text = "Z")

    def updateSocketVisibility(self):
        self.inputs["Location"].hide = not (self.useLocation[0] or self.useLocation[1] or self.useLocation[2])
        self.inputs["Rotation"].hide = not (self.useRotation[0] or self.useRotation[1] or self.useRotation[2])
        self.inputs["Scale"].hide = not (self.useScale[0] or self.useScale[1] or self.useScale[2])

    def getExecutionCode(self):
        useLoc = self.useLocation
        useRot = self.useRotation
        useScale = self.useScale

        codeLines = []
        codeLines.append("if %object% is not None:")

        # location
        if useLoc[0] and useLoc[1] and useLoc[2]:
            codeLines.append("    %object%.location = %location%")
        else:
            for i in range(3):
                if useLoc[i]: codeLines.append("    %object%.location["+str(i)+"] = %location%["+str(i)+"]")

        # rotation
        if useRot[0] and useRot[1] and useRot[2]:
            codeLines.append("    %object%.rotation_euler = %rotation%")
        else:
            for i in range(3):
                if useRot[i]: codeLines.append("    %object%.rotation_euler["+str(i)+"] = %rotation%["+str(i)+"]")

        # scale
        if useScale[0] and useScale[1] and useScale[2]:
            codeLines.append("    %object%.scale = %scale%")
        else:
            for i in range(3):
                if useScale[i]: codeLines.append("    %object%.scale["+str(i)+"] = %scale%["+str(i)+"]")

        if not any((useLoc[0], useLoc[1], useLoc[2],
                   useRot[0], useRot[1], useRot[2],
                   useScale[0], useScale[1], useScale[2])):
            codeLines = []

        codeLines.append("$object$ = %object%")
        return "\n".join(codeLines)
