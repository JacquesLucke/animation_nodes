import bpy
from mathutils import Vector
from ... events import propertyChanged
from ... base_types.node import AnimationNode

trackAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")]
upAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z")]

class DirectionToRotation(bpy.types.Node, AnimationNode):
    bl_idname = "mn_DirectionToRotation"
    bl_label = "Direction to Rotation"

    inputNames = { "Direction" : "direction" }
    outputNames = { "Rotation" : "rotation" }

    trackAxis = bpy.props.EnumProperty(items = trackAxisItems, update = propertyChanged, default = "Z")
    upAxis = bpy.props.EnumProperty(items = upAxisItems, update = propertyChanged, default = "X")

    def create(self):
        self.inputs.new("mn_VectorSocket", "Direction")
        self.outputs.new("mn_VectorSocket", "Rotation")
        self.width += 20

    def draw_buttons(self, context, layout):
        layout.prop(self, "trackAxis", expand = True)
        layout.prop(self, "upAxis", expand = True)

        if self.trackAxis == self.upAxis:
            layout.label("Must be different", icon = "ERROR")

    def execute(self, direction):
        if self.trackAxis == self.upAxis: return Vector((0, 0, 0))
        return Vector((direction.to_track_quat(self.trackAxis, self.upAxis).to_euler()))
