import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... algorithms.rotations import eulerToDirection
from ... data_structures cimport BaseFalloff, DoubleList
from . constant_falloff import ConstantFalloff
from . interpolate_falloff import InterpolateFalloff
from . directional_falloff import UniDirectionalFalloff
from . point_distance_falloff import PointDistanceFalloff

falloffTypeItems = [
    ("SPHERE", "Sphere", "", 0),
    ("DIRECTIONAL", "Directional", "", 1)
]

axisDirectionItems = [(axis, axis, "") for axis in ("X", "Y", "Z", "-X", "-Y", "-Z")]

class ObjectControllerFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectControllerFalloffNode"
    bl_label = "Object Controller Falloff"

    falloffType = EnumProperty(name = "Falloff Type", items = falloffTypeItems,
        update = AnimationNode.updateSockets)

    axisDirection = EnumProperty(name = "Axis Direction", default = "Z",
        items = axisDirectionItems, update = propertyChanged)

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        if self.falloffType == "SPHERE":
            self.newInput("Float", "Falloff Width", "falloffWidth", value = 1.0)
        self.newInput("Interpolation", "Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        col = layout.column()
        col.prop(self, "falloffType", text = "Type")
        if self.falloffType == "DIRECTIONAL":
            col.row().prop(self, "axisDirection", expand = True)

    def getExecutionFunctionName(self):
        if self.falloffType == "SPHERE":
            return "execute_Sphere"
        elif self.falloffType == "DIRECTIONAL":
            return "execute_Directional"

    def execute_Sphere(self, object, falloffWidth, interpolation):
        if object is None:
            return ConstantFalloff(1)

        matrix = object.matrix_world
        center = matrix.to_translation()
        size = abs(matrix.to_scale().x)
        falloff = PointDistanceFalloff(center, size, falloffWidth)
        return InterpolateFalloff(falloff, interpolation)

    def execute_Directional(self, object, interpolation):
        if object is None:
            return ConstantFalloff(1)

        matrix = object.matrix_world
        location = matrix.to_translation()
        size = max(matrix.to_scale().x, 0.0001)
        direction = eulerToDirection(matrix.to_euler(), self.axisDirection)
        
        falloff = UniDirectionalFalloff(location, direction, size)
        return InterpolateFalloff(falloff, interpolation)
