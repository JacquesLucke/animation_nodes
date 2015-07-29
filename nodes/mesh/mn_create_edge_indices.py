import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
import math

class mn_CreateEdgeIndices(bpy.types.Node, AnimationNode):
    bl_idname = "mn_CreateEdgeIndices"
    bl_label = "Create Edge Indices"
    node_category = "Mesh"
    isDetermined = True
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_IntegerSocket", "Index 1").number = 0
        self.inputs.new("mn_IntegerSocket", "Index 2").number = 1
        self.outputs.new("mn_EdgeIndicesSocket", "Edge Indices")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        pass
        
    def getInputSocketNames(self):
        return {"Index 1" : "index1",
                "Index 2" : "index2"}
    def getOutputSocketNames(self):
        return {"Edge Indices" : "edgeIndices"}
        
    def useInLineExecution(self):
        return True
    def getInLineExecutionString(self, outputUse):
        return "$edgeIndices$ = (%index1%, %index2%)"
