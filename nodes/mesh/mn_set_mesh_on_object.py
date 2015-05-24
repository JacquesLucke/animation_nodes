import bpy, bmesh
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.mesh import *

class mn_SetMeshOnObject(Node, AnimationNode):
    bl_idname = "mn_SetMeshOnObject"
    bl_label = "Set Mesh on Object"
    
    def init(self, context):
        forbidCompiling()
        socket = self.inputs.new("mn_ObjectSocket", "Object")
        socket.showName = False
        socket.createObject = True
        self.inputs.new("mn_MeshSocket", "Mesh")
        self.outputs.new("mn_ObjectSocket", "Object")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        pass
        
    def getInputSocketNames(self):
        return {"Object" : "object",
                "Mesh" : "bm"}
    def getOutputSocketNames(self):
        return {"Object" : "object"}
        
    def execute(self, object, bm):
        if object is None: return object
        if object.type == "MESH":
            if object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode = "OBJECT")
            if object.mode == "OBJECT":
                bm.to_mesh(object.data)
        return object