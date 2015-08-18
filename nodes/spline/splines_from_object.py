import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... data_structures.splines.from_blender import createSplinesFromBlenderObject

class SplinesFromObject(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplinesFromObject"
    bl_label = "Splines from Object"

    inputNames = { "Object" : "object" }
    outputNames = { "Splines" : "splines" }

    useWorldTransform = BoolProperty(
        name = "Use World Transform",
        description = "Use the position in global space",
        default = True, update = propertyChanged)

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object").showName = False
        self.outputs.new("an_SplineListSocket", "Splines")

    def draw(self, layout):
        layout.prop(self, "useWorldTransform")

    def execute(self, object):
        splines = createSplinesFromBlenderObject(object)
        if self.useWorldTransform:
            for spline in splines:
                spline.transform(object.matrix_world)
        return splines
