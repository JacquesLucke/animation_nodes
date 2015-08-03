import bpy
from ... base_types.node import AnimationNode
from ... data_structures.splines.to_blender import setSplinesOnBlenderObject

class SetSplinesOnObject(bpy.types.Node, AnimationNode):
    bl_idname = "mn_SetSplinesOnObject"
    bl_label = "Set Splines on Object"

    inputNames = { "Object" : "object",
                   "Splines" : "splines" }

    outputNames = { "Object" : "object" }

    def create(self):
        socket = self.inputs.new("mn_ObjectSocket", "Object")
        socket.showName = False
        socket.objectCreationType = "CURVE"
        self.inputs.new("mn_SplineListSocket", "Splines").showObjectInput = False
        self.outputs.new("mn_ObjectSocket", "Object")

    def execute(self, object, splines):
        setSplinesOnBlenderObject(object, splines)
        return object
