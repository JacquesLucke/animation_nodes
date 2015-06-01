import bpy
import mathutils
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

class mn_SeparateVectorList(Node, AnimationNode):
    bl_idname = "mn_SeparateVectorList"
    bl_label = "Separate Vector List"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorListSocket", "Vector List")
        self.outputs.new("mn_FloatListSocket", "List X")
        self.outputs.new("mn_FloatListSocket", "List Y")
        self.outputs.new("mn_FloatListSocket", "List Z")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Vector List" : "vectorList"}

    def getOutputSocketNames(self):
        return {"List X" : "listX",
                "List Y" : "listY",
                "List Z" : "listZ"}

    def execute(self, vectorList):
        listX = []
        listY = []
        listZ = []
            
        try:
            lenList = len(vectorList)
            for iList in range(lenList):
                v = vectorList[iList]
                listX.append(v.x)
                listY.append(v.y)
                listZ.append(v.z)
        except: pass
        
        return listX, listY, listZ
