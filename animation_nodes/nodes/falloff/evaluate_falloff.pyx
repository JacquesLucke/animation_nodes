import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
from ... data_structures cimport FalloffEvaluator, DoubleList, CList

falloffTypeItems = [
    ("Location", "Location", "", "", 0),
    ("Transformation Matrix", "Transformation Matrix", "", "", 1)
]

class EvaluateFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_EvaluateFalloffNode"
    bl_label = "Evaluate Falloff"

    falloffType = EnumProperty(name = "Falloff Type",
        items = falloffTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Falloff", "Falloff", "falloff")
        if self.falloffType == "Location":
            self.newInput("Vector List", "Locations", "locations")
        elif self.falloffType == "Transformation Matrix":
            self.newInput("Matrix List", "Matrices", "matrices")
        self.newOutput("Float List", "Strengths", "strengths")

    def draw(self, layout):
        layout.prop(self, "falloffType", text = "")

    def execute(self, falloff, myList):
        cdef FalloffEvaluator _falloff = falloff.getEvaluator(self.falloffType)
        return self.evaluate_CList(_falloff, myList)

    def evaluate_CList(self, FalloffEvaluator _falloff, CList myList):
        cdef long i
        cdef char *data = <char*>myList.getPointer()
        cdef int elementSize = myList.getElementSize()
        cdef DoubleList strengths = DoubleList(length = myList.getLength())
        for i in range(myList.getLength()):
            strengths.data[i] = _falloff.evaluate(data + i * elementSize, i)
        return strengths
