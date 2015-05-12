import bpy, random, mathutils
from bpy.types import Node
from mathutils import Vector
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ParticleInfo(Node, AnimationNode):
    bl_idname = "mn_ParticleInfo"
    bl_label = "Particle Info"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ParticleSocket", "Particle")
        self.outputs.new("mn_VectorSocket", "Location")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Particle" : "particle"}
    def getOutputSocketNames(self):
        return {"Location" : "location"}

    def execute(self, particle):
        if not particle: return Vector((0, 0, 0))
        return particle.location
        

