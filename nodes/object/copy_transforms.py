import bpy
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... utils.fcurve import (getArrayValueAtFrame,
                              getSingleValueOfArrayAtFrame,
                              getMultipleValuesOfArrayAtFrame)

class CopyTransformsNode(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CopyTransformsNode"
    bl_label = "Copy Transforms"

    inputNames = { "From" : "fromObject",
                   "To" : "toObject",
                   "Frame" : "frame" }

    outputNames = { "To" : "toObject" }

    useLocation = bpy.props.BoolVectorProperty(update = propertyChanged)
    useRotation = bpy.props.BoolVectorProperty(update = propertyChanged)
    useScale = bpy.props.BoolVectorProperty(update = propertyChanged)

    frameTypes = [
        ("OFFSET", "Offset", ""),
        ("ABSOLUTE", "Absolute", "") ]
    frameTypesProperty = bpy.props.EnumProperty(name = "Frame Type", items = frameTypes, default = "OFFSET", update = propertyChanged)

    def create(self):
        self.inputs.new("mn_ObjectSocket", "From")
        self.inputs.new("mn_ObjectSocket", "To")
        self.inputs.new("mn_FloatSocket", "Frame")
        self.outputs.new("mn_ObjectSocket", "To")
        self.width = 200

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

        layout.prop(self, "frameTypesProperty")

    def execute(self, fromObject, toObject, frame):
        if fromObject is None or toObject is None:
            return toObject

        if self.frameTypesProperty == "OFFSET":
            frame += bpy.context.scene.frame_current

        self.copyLocation(fromObject, toObject, frame)
        self.copyRotation(fromObject, toObject, frame)
        self.copyScale(fromObject, toObject, frame)

        return toObject

    def copyLocation(self, fromObject, toObject, frame):
        use = tuple(self.useLocation)
        if use[0] and use[1] and use[2]:
            toObject.location = getArrayValueAtFrame(fromObject, "location", frame)
        elif use[0] and use[1]:
            toObject.location[0], toObject.location[1] = getMultipleValuesOfArrayAtFrame(fromObject, "location", [0, 1], frame)
        elif use[0] and use[2]:
            toObject.location[0], toObject.location[2] = getMultipleValuesOfArrayAtFrame(fromObject, "location", [0, 2], frame)
        elif use[1] and use[2]:
            toObject.location[1], toObject.location[2] = getMultipleValuesOfArrayAtFrame(fromObject, "location", [1, 2], frame)
        else:
            for i in range(3):
                if use[i]: toObject.location[i] = getSingleValueOfArrayAtFrame(fromObject, "location", index = i, frame = frame)

    def copyRotation(self, fromObject, toObject, frame):
        use = self.useRotation

        if use[0] and use[1] and use[2]:
            toObject.rotation_euler = getArrayValueAtFrame(fromObject, "rotation_euler", frame)
        elif use[0] and use[1]:
            toObject.rotation_euler[0], toObject.rotation_euler[1] = getMultipleValuesOfArrayAtFrame(fromObject, "rotation_euler", [0, 1], frame)
        elif use[0] and use[2]:
            toObject.rotation_euler[0], toObject.rotation_euler[2] = getMultipleValuesOfArrayAtFrame(fromObject, "rotation_euler", [0, 2], frame)
        elif use[1] and use[2]:
            toObject.rotation_euler[1], toObject.rotation_euler[2] = getMultipleValuesOfArrayAtFrame(fromObject, "rotation_euler", [1, 2], frame)
        else:
            for i in range(3):
                if use[i]: toObject.rotation_euler[i] = getSingleValueOfArrayAtFrame(fromObject, "rotation_euler", index = i, frame = frame)

    def copyScale(self, fromObject, toObject, frame):
        use = self.useScale
        if use[0] and use[1] and use[2]:
            toObject.scale = getArrayValueAtFrame(fromObject, "scale", frame)
        elif use[0] and use[1]:
            toObject.scale[0], toObject.scale[1] = getMultipleValuesOfArrayAtFrame(fromObject, "scale", [0, 1], frame)
        elif use[0] and use[2]:
            toObject.scale[0], toObject.scale[2] = getMultipleValuesOfArrayAtFrame(fromObject, "scale", [0, 2], frame)
        elif use[1] and use[2]:
            toObject.scale[1], toObject.scale[2] = getMultipleValuesOfArrayAtFrame(fromObject, "scale", [1, 2], frame)
        else:
            for i in range(3):
                if use[i]: toObject.scale[i] = getSingleValueOfArrayAtFrame(fromObject, "scale", index = i, frame = frame)
