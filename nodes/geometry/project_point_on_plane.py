import bpy
from bpy.props import *
from ... base_types.node import AnimationNode

class ProjectPointOnPlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ProjectPointOnPlaneNode"
    bl_label = "Project Point on Plane"

    def create(self):
        self.width = 160
        self.inputs.new("an_VectorSocket", "Point", "point")
        self.inputs.new("an_VectorSocket", "Plane Point", "planePoint").value = (1, 0, 0)
        self.inputs.new("an_VectorSocket", "Plane Normal", "planeNormal").value = (0, 0, 1)
        
        self.outputs.new("an_VectorSocket", "Projection", "projection")
        self.outputs.new("an_FloatSocket", "Distance to Plane", "distance")
        
    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not any(isLinked.values()): return ""
        
        if any(isLinked.values()):yield "plane_co, plane_no = " + getPlane()
        if isLinked["projection"]:
            yield "int = mathutils.geometry.intersect_line_plane(point, point + plane_no, plane_co, plane_no, False)"
            yield "projection = mathutils.Vector((0, 0, 0)) if int is None else int"
        if isLinked["distance"]: yield "distance = mathutils.geometry.distance_point_to_plane(point, plane_co, plane_no)"
 
    def getUsedModules(self):
        return ["mathutils"]

def getPlane():
    return "planePoint, planeNormal if planeNormal.length_squared != 0 else mathutils.Vector((0, 0, 1))"
