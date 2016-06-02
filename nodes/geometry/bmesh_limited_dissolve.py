import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

class BMeshLimitedDissolveNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_BMeshLimitedDissolve"
    bl_label = "Limited Dissolve BMesh"
    bl_width_default = 160

    def create(self):
        self.newInput("BMesh", "BMesh", "bm", dataIsModified = True)
        self.newInput("Float", "Angle Limit", "angleLimit", value = 30.0)
        self.newInput("Boolean", "Dissolve Boundries", "dissolveBoundries", value = False)
        self.newOutput("BMesh", "BMesh", "bm")

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return

        if isLinked["bm"]: 
            yield "bmesh.ops.dissolve_limit(bm, verts = bm.verts, edges = bm.edges,"
            yield "    angle_limit = math.radians(angleLimit),"
            yield "    use_dissolve_boundaries = dissolveBoundries)"
        
    def getUsedModules(self):
        return ["math", "bmesh"]
