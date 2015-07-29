import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import allowCompiling, forbidCompiling

class mn_MakeObjectSmooth(bpy.types.Node, AnimationNode):
    bl_idname = "mn_MakeObjectSmooth"
    bl_label = "Make Object Smooth"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.inputs.new("mn_BooleanSocket", "Smooth")
        self.outputs.new("mn_ObjectSocket", "Object")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object",
                "Smooth" : "smooth"}
    def getOutputSocketNames(self):
        return {"Object" : "object"}
        
    def execute(self, object, smooth):
        if getattr(object, "type", "") == "MESH":
            for polygon in object.data.polygons:
                polygon.use_smooth = smooth
        return object