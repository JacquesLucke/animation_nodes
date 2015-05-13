import bpy, random, mathutils
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ObjectParticleSystemsInput(Node, AnimationNode):
    bl_idname = "mn_ObjectParticleSystemsInput"
    bl_label = "Particle Systems Input"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_ParticleSystemSocket", "Active")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object"}
    def getOutputSocketNames(self):
        return {"Active" : "active"}

    def execute(self, object):
        if not object: return None
        active = object.particle_systems.active
        return active
        

