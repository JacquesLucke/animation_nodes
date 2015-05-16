import bpy
import mathutils
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_CombineVectorList(Node, AnimationNode):
    bl_idname = "mn_CombineVectorList"
    bl_label = "Combine Vector List"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatListSocket", "List X")
        self.inputs.new("mn_FloatListSocket", "List Y")
        self.inputs.new("mn_FloatListSocket", "List Z")
        self.outputs.new("mn_VectorListSocket", "Vector List")
        allowCompiling()

    def getInputSocketNames(self):
        return {"List X" : "listX",
                "List Y" : "listY",
                "List Z" : "listZ"}

    def getOutputSocketNames(self):
        return {"Vector List" : "vectorList"}

    def canExecute(self, listX, listY, listZ):
        if len(listX) != len(listY): return False
        if len(listY) != len(listZ): return False
            
        return True

    def execute(self, listX, listY, listZ):
        vectorList = []
        if not self.canExecute(listX, listY, listZ):
            return vectorList
            
        try:
            lenLists = len(listX)
            for iLists in range(lenLists):
                vectorList.append(mathutils.Vector((listX[iLists], listY[iLists], listZ[iLists])))
        except: pass
        
        return vectorList
