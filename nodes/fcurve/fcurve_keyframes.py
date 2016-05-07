import bpy
from ... base_types.node import AnimationNode
from ... data_structures import FloatList, DoubleList
from ... algorithms.list_creation import floatListToDoubleList as toDoubleList

class FCurveKeyframesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FCurveKeyframesNode"
    bl_label = "FCurve Keyframes"

    def create(self):
        self.newInput("FCurve", "FCurve", "fCurve")
        self.newOutput("Float List", "Keyframes Frames", "keyframesFrames")
        self.newOutput("Float List", "Keyframes Values", "keyframesValues")

    def execute(self, fCurve):
        if fCurve is None:
            return DoubleList(), DoubleList()

        allValues = FloatList(len(fCurve.keyframe_points) * 2)
        fCurve.keyframe_points.foreach_get("co", allValues.getMemoryView())
        return toDoubleList(allValues[0::2]), toDoubleList(allValues[1::2])
