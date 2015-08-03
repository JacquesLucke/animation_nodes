import bpy
from ... base_types.node import AnimationNode

class CreateEdgeIndices(bpy.types.Node, AnimationNode):
    bl_idname = "an_CreateEdgeIndices"
    bl_label = "Create Edge Indices"
    isDetermined = True

    inputNames = { "Index 1" : "index1",
                   "Index 2" : "index2" }

    outputNames = { "Edge Indices" : "edgeIndices" }

    def create(self):
        self.inputs.new("an_IntegerSocket", "Index 1").value = 0
        self.inputs.new("an_IntegerSocket", "Index 2").value = 1
        self.outputs.new("an_EdgeIndicesSocket", "Edge Indices")

    def getExecutionCode(self, outputUse):
        return "$edgeIndices$ = (%index1%, %index2%)"
