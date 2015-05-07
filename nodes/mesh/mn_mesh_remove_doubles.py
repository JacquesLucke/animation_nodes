import bpy, bmesh
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_MeshRemoveDoubles(Node, AnimationNode):
    bl_idname = "mn_MeshRemoveDoubles"
    bl_label = "Mesh Remove Doubles"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_MeshSocket", "Mesh")
        socket = self.inputs.new("mn_FloatSocket", "Distance")
        socket.number = 0.0001
        socket.setMinMax(0.0, 10000.0)
        self.outputs.new("mn_MeshSocket", "Mesh")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Mesh" : "bm",
                "Distance" : "distance"}
    def getOutputSocketNames(self):
        return {"Mesh" : "mesh"}
        
    def execute(self, bm, distance):
        bmesh.ops.remove_doubles(bm, verts = bm.verts, dist = distance)
        return bm