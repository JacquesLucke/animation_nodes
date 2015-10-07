import bpy
from bpy.props import *
from mathutils import Vector, Matrix
from ... events import propertyChanged, executionCodeChanged
from ... base_types.node import AnimationNode

# equivalent to to_track_quat (direction to rotation), but extra fixed rotation around track axis (direction)
# default Z / X gives standard polygon dupli orientation: Z = normal, X = vertex1  -vertex0
#   by o.g. for Animation Nodes, after long discussions on forum, using matrix as Bartek Skorupa shows here:
#   http://blenderartists.org/forum/showthread.php?366376-Calculating-XYZ-Euler-rotation-values-for-arbitrary-plane&p=2845715&viewfull=1#post2845715

trackAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")] 
guideAxisItems = [(axis, axis, "") for axis in ("X", "Y", "Z")]

class GuidedTrack(bpy.types.Node, AnimationNode):
    bl_idname = "an_GuidedTrack"
    bl_label = "guided_track"

    trackAxis = EnumProperty(items = trackAxisItems, update = executionCodeChanged, default = "Z",
                            description = "Track Axis (or Normal, for distribution on polygons)")
    guideAxis = EnumProperty(items = guideAxisItems, update = executionCodeChanged, default = "X",
                            description = "Guided Axis, set rotation around Track Axis (vertex 0,1 to X is a standard for distribution on polygons)")
    
    def create(self):
        self.inputs.new("an_VectorSocket", "Direction", "direction")
        self.inputs.new("an_VectorSocket", "Guide", "guide")
        self.outputs.new("an_VectorSocket", "Rotation Vector", "rotationVector")
        self.outputs.new("an_MatrixSocket", "Rotation Matrix", "rotationMatrix")
        
        self.width += 20

    def draw(self, layout):
        col = layout.column(align = True)
        row = col.row(align = True)
        row.prop(self, "trackAxis", expand = True)
        row = col.row(align = True)
        row.prop(self, "guideAxis", expand = True)

        if self.trackAxis == self.guideAxis or self.trackAxis == "-" + self.guideAxis: 
            layout.label("Must be different", icon = "ERROR")
    
    def getExecutionCode(self):
        lines = []
        lines.append("mat3x3 = mathutils.Matrix().to_3x3()")
        lines.append("mat3x3.col[0] = mathutils.Vector((1, 0, 0))")
        lines.append("mat3x3.col[1] = mathutils.Vector((0, 1, 0))")
        lines.append("mat3x3.col[2] = mathutils.Vector((0, 0, 1))")
        
        if self.trackAxis != self.guideAxis and self.trackAxis != ("-" + self.guideAxis):
            tAx = self.trackAxis
            gAx = self.guideAxis
            
            #direction
            lines.append("if direction != mathutils.Vector((0, 0, 0)): z = direction.normalized()")
            if tAx == "X":    lines.append("else: z = mathutils.Vector((1, 0, 0))")
            elif tAx == "Y":  lines.append("else: z = mathutils.Vector((0, 1, 0))")
            elif tAx == "Z":  lines.append("else: z = mathutils.Vector((0, 0, 1))") # Z/X default, thus the notation
            elif tAx == "-X": lines.append("else: z = mathutils.Vector((1, 0, 0))")
            elif tAx == "-Y": lines.append("else: z = mathutils.Vector((0, 1, 0))")
            elif tAx == "-Z": lines.append("else: z = mathutils.Vector((0, 0, 1))")
            
            #guide
            lines.append("if guide != mathutils.Vector((0, 0, 0)) and z.cross(guide) != mathutils.Vector((0, 0, 0)): gui = guide.normalized()")
            if gAx == "X":    lines.append("else: gui = mathutils.Vector((1, 0, 0))")
            elif gAx == "Y":  lines.append("else: gui = mathutils.Vector((0, 1, 0))")
            elif gAx == "Z":  lines.append("else: gui = mathutils.Vector((0, 0, 1))")
            
            lines.append("y = (z.cross(gui)).normalized()") #if z.cross(guide) != mathutils.Vector((0, 0, 0)) else mathutils.Vector((0, 1, 0))")
            lines.append("x = y.cross(z)")  #guide as perpendicular to dir
            
            # the escapes here are needed only for the matrix, to not fall to scale 0
            #lines.append("z = direction.normalized() if direction != mathutils.Vector((0, 0, 0)) else mathutils.Vector((0, 0, 1))")          #direction
            #lines.append("y = (z.cross(guide)).normalized() if guide != mathutils.Vector((0, 0, 0)) and guide.normalized() != z else mathutils.Vector((0, 1, 0))")
            #lines.append("x = y.cross(z)")  #guide as perpendicular to dir
            
            tAx = self.trackAxis
            gAx = self.guideAxis
            
            if tAx == "X":    lines.append("(mx, my, mz) = ( z,-y, x)") if gAx == "Z" else lines.append("(mx, my, mz) = ( z, x, y)")
            elif tAx == "Y":  lines.append("(mx, my, mz) = ( y, z, x)") if gAx == "Z" else lines.append("(mx, my, mz) = ( x, z,-y)") 
            elif tAx == "Z":  lines.append("(mx, my, mz) = ( x, y, z)") if gAx == "X" else lines.append("(mx, my, mz) = (-y, x, z)") #Z/X default, thus the notation
            elif tAx == "-X": lines.append("(mx, my, mz) = (-z, y, x)") if gAx == "Z" else lines.append("(mx, my, mz) = (-z, x,-y)") 
            elif tAx == "-Y": lines.append("(mx, my, mz) = (-y,-z, x)") if gAx == "Z" else lines.append("(mx, my, mz) = ( x,-z, y)") 
            elif tAx == "-Z": lines.append("(mx, my, mz) = ( x,-y,-z)") if gAx == "X" else lines.append("(mx, my, mz) = ( y, x,-z)")
            
            lines.append("mat3x3.col[0] = mx")
            lines.append("mat3x3.col[1] = my")
            lines.append("mat3x3.col[2] = mz")

        lines.append("rotationVector = mathutils.Vector((mat3x3.to_euler()))")
        lines.append("rotationMatrix = mat3x3.to_4x4()")
        
        return lines
    
    def getUsedModules(self):
        return ["mathutils"]
