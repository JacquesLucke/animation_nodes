import bpy
from bpy.props import *
from mathutils import Vector
from ... events import executionCodeChanged
from ... base_types.node import AnimationNode

trackAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")]
guideAxisItems  = [(axis, axis, "") for axis in ("X", "Y", "Z")]

class DirectionToRotationNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DirectionToRotationNode"
    bl_label = "Direction to Rotation"

    trackAxis = EnumProperty(items = trackAxisItems, update = executionCodeChanged, default = "Z")
    guideAxis = EnumProperty(items = guideAxisItems, update = executionCodeChanged, default = "X")

    def create(self):
        self.inputs.new("an_VectorSocket", "Direction", "direction")
        self.inputs.new("an_VectorSocket", "Guide", "guide").value = [0.0, 0.0, 1.0]
        self.outputs.new("an_EulerSocket", "Euler Rotation", "eulerRotation")
        self.width += 20

    def draw(self, layout):
        layout.prop(self, "trackAxis", expand = True)
        layout.prop(self, "guideAxis", expand = True)

        if self.trackAxis[-1:] == self.guideAxis[-1:]:
            layout.label("Must be different", icon = "ERROR")

    def getExecutionCode(self):
        if self.trackAxis[-1:] == self.guideAxis[-1:]:
            yield "eulerRotation = mathutils.Euler((0, 0, 0), 'XYZ')"
            return
        
        yield "zero, worldX, worldY, worldZ = " + getWorldVectors()

        yield "if direction != zero: z = direction.normalized()"
        if "X" in self.trackAxis: yield "else: z = worldX"
        if "Y" in self.trackAxis: yield "else: z = worldY"
        if "Z" in self.trackAxis: yield "else: z = worldZ"

        yield "if guide != zero and z.cross(guide) != zero: y = z.cross(guide.normalized())"
        if "X" == self.guideAxis: yield "else: y = z.cross(worldX) if z.cross(worldX) != zero else worldZ"
        if "Y" == self.guideAxis: yield "else: y = z.cross(worldY) if z.cross(worldY) != zero else worldZ"
        if "Z" == self.guideAxis: yield "else: y = z.cross(worldZ) if z.cross(worldZ) != zero else worldY"

        yield "x = y.cross(z)"

        yield "mx, my, mz = " + getAxesChange(self.trackAxis, self.guideAxis)

        yield "mat3x3 = mathutils.Matrix().to_3x3()"
        yield "mat3x3.col[0], mat3x3.col[1], mat3x3.col[2] = mx, my, mz"
        yield "eulerRotation = mat3x3.to_euler()"

    def getUsedModules(self):
        return ["mathutils"]

def getAxesChange(track, guide):
    if track == "X":    a = "( z,-y, x)" if guide == "Z" else "( z, x, y)"
    elif track == "Y":  a = "( y, z, x)" if guide == "Z" else "( x, z,-y)"
    elif track == "Z":  a = "( x, y, z)" if guide == "X" else "(-y, x, z)"
    elif track == "-X": a = "(-z, y, x)" if guide == "Z" else "(-z, x,-y)"
    elif track == "-Y": a = "(-y,-z, x)" if guide == "Z" else "( x,-z, y)"
    elif track == "-Z": a = "( x,-y,-z)" if guide == "X" else "( y, x,-z)"
    return a

def getWorldVectors():
    o = "mathutils.Vector((0, 0, 0))"
    x = "mathutils.Vector((1, 0, 0))"
    y = "mathutils.Vector((0, 1, 0))"
    z = "mathutils.Vector((0, 0, 1))"
    return o + ", " + x + ", "+ y + ", "+ z
