import bpy
from bpy.props import *
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

class an_ObjectTransformsOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectTransformsOutputNode"
    bl_label = "Object Transforms Output"

    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        executionCodeChanged()

    useLocation = BoolVectorProperty(update = checkedPropertiesChanged)
    useRotation = BoolVectorProperty(update = checkedPropertiesChanged)
    useScale = BoolVectorProperty(update = checkedPropertiesChanged)

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Vector", "Location", "location")
        self.newInput("Euler", "Rotation", "rotation")
        self.newInput("Vector", "Scale", "scale", value = (1, 1, 1))
        self.newOutput("Object", "Object", "object")
        self.updateSocketVisibility()

    def draw(self, layout):
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

        if not any((*useLoc, *useRot, *useScale)):
            return

        yield "if object is not None:"

        # Location
        if all((*useLoc, )):
            yield "    object.location = location"
        else:
            for i in range(3):
                if useLoc[i]: yield "    object.location["+str(i)+"] = location["+str(i)+"]"

        # Rotation
        if all((*useRot, )):
            yield "    object.rotation_euler = rotation"
        else:
            for i in range(3):
                if useRot[i]: yield "    object.rotation_euler["+str(i)+"] = rotation["+str(i)+"]"

        # Scale
        if all((*useScale, )):
            yield "    object.scale = scale"
        else:
            for i in range(3):
                if useScale[i]: yield "    object.scale["+str(i)+"] = scale["+str(i)+"]"

    def getBakeCode(self):
        yield "if object is not None:"

        for i in range(3):
            if self.useLocation[i]:
                yield "    object.keyframe_insert('location', index = {})".format(i)

        for i in range(3):
            if self.useRotation[i]:
                yield "    object.keyframe_insert('rotation_euler', index = {})".format(i)

        for i in range(3):
            if self.useScale[i]:
                yield "    object.keyframe_insert('scale', index = {})".format(i)
