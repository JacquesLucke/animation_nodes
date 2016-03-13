import bpy
from ... base_types.node import AnimationNode

class DistanceVectorToPlaneNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DistanceVectorToPlaneNode"
    bl_label = "Distance Vector to Plane"
    bl_width_default = 160

    def create(self):
        self.inputs.new("an_VectorSocket", "Vector", "vector")
        self.inputs.new("an_VectorSocket", "Point on Plane", "planePoint")
        self.inputs.new("an_VectorSocket", "Plane Normal", "planeNormal").value = (0, 0, 1)
        self.outputs.new("an_FloatSocket", "Distance", "distance")

    def getExecutionCode(self):
        return "distance = mathutils.geometry.distance_point_to_plane(vector, planePoint, planeNormal)"

    def getUsedModules(self):
        return ["mathutils"]
