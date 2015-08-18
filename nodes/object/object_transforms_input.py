import bpy
from bpy.props import *
from mathutils import Vector
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... utils.fcurve import getArrayValueAtFrame

frameTypes = [
    ("OFFSET", "Offset", ""),
    ("ABSOLUTE", "Absolute", "") ]

class ObjectTransformsInput(bpy.types.Node, AnimationNode):
    bl_idname = "an_ObjectTransformsInput"
    bl_label = "Object Transforms Input"
    outputUseParameterName = "usedOutputs"

    frameTypesProperty = EnumProperty(
        name = "Frame Type", default = "OFFSET",
        items = frameTypes, update = propertyChanged)

    def create(self):
        self.inputs.new("an_ObjectSocket", "Object", "object").showName = False
        self.inputs.new("an_FloatSocket", "Frame", "frame")
        self.outputs.new("an_VectorSocket", "Location", "location")
        self.outputs.new("an_VectorSocket", "Rotation", "rotation")
        self.outputs.new("an_VectorSocket", "Scale", "scale")

    def draw(self, layout):
        layout.prop(self, "frameTypesProperty")

    def execute(self, usedOutputs, object, frame):
        location = (0, 0, 0)
        rotation = (0, 0, 0)
        scale = (1, 1, 1)

        if object is None:
            return Vector(location), Vector(rotation), Vector(scale)

        currentFrame = bpy.context.scene.frame_current
        if self.frameTypesProperty == "OFFSET":
            frame += currentFrame

        if frame == currentFrame:
            location = object.location
            rotation = object.rotation_euler
            scale = object.scale
        else:
            if usedOutputs["Location"]:
                location = getArrayValueAtFrame(object, "location", frame)
            if usedOutputs["Rotation"]:
                rotation = getArrayValueAtFrame(object, "rotation_euler", frame)
            if usedOutputs["Scale"]:
                scale = getArrayValueAtFrame(object, "scale", frame)

        return Vector(location), Vector(rotation), Vector(scale)
