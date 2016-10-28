import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures cimport BaseFalloff, DoubleList
from . constant_falloff import ConstantFalloff
from . interpolate_falloff import InterpolateFalloff
from . point_distance_falloff import PointDistanceFalloff

falloffTypeItems = [
    ("SPHERE", "Sphere", "", 0)
]

class ObjectControllerFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectControllerFalloffNode"
    bl_label = "Object Controller Falloff"

    falloffType = EnumProperty(name = "Falloff Type", items = falloffTypeItems)

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        if self.falloffType == "SPHERE":
            self.newInput("Float", "Falloff Width", "falloffWidth")
        self.newInput("Interpolation", "Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        layout.prop(self, "falloffType")

    def getExecutionFunctionName(self):
        if self.falloffType == "SPHERE":
            return "execute_Sphere"

    def execute_Sphere(self, object, falloffWidth, interpolation):
        if object is None:
            return ConstantFalloff(0)

        matrix = object.matrix_world
        center = matrix.to_translation()
        size = abs(matrix.to_scale().x)
        falloff = PointDistanceFalloff(center, size, falloffWidth)
        return InterpolateFalloff(falloff, interpolation)
