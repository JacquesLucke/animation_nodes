import bpy
from bpy.types import Node
from mathutils import Vector
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

trackAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")]
upAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z")]

class mn_DirectionToRotation(Node, AnimationNode):
    bl_idname = "mn_DirectionToRotation"
    bl_label = "Direction to Rotation"
    
    trackAxis = bpy.props.EnumProperty(items = trackAxisItems, update = nodeTreeChanged, default = "Z")
    upAxis = bpy.props.EnumProperty(items = upAxisItems, update = nodeTreeChanged, default = "X")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "Direction")
        self.outputs.new("mn_VectorSocket", "Rotation")
        self.width += 20
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "trackAxis", expand = True)
        layout.prop(self, "upAxis", expand = True)
        
        if self.trackAxis == self.upAxis:
            layout.label("Must be different", icon = "ERROR")
        
    def getInputSocketNames(self):
        return {"Direction" : "direction"}
    def getOutputSocketNames(self):
        return {"Rotation" : "rotation"}

    def execute(self, direction):
        if self.trackAxis == self.upAxis: return Vector((0, 0, 0))
        return Vector((direction.to_track_quat(self.trackAxis, self.upAxis).to_euler()))
        

