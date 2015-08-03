import bpy
from ... base_types.node import AnimationNode
from ... data_structures.splines.to_blender import setSplinesOnBlenderObject

class SetSplinesOnObject(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetSplinesOnObject"
    bl_label = "Set Splines on Object"

    inputNames = { "Object" : "object",
                   "Splines" : "splines" }

    outputNames = { "Object" : "object" }

    def create(self):
        socket = self.inputs.new("an_ObjectSocket", "Object")
        socket.showName = False
        socket.objectCreationType = "CURVE"
        self.inputs.new("an_SplineListSocket", "Splines").showObjectInput = False
        self.outputs.new("an_ObjectSocket", "Object")

    def execute(self, object, splines):
        setSplinesOnBlenderObject(object, splines)
        return object
