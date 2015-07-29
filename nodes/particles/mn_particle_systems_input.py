import bpy, random, mathutils
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling


class mn_ParticleSystemsInput(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ParticleSystemsInput"
    bl_label = "Particle Systems Input"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_ParticleSystemListSocket", "Particle Systems")
        self.outputs.new("mn_ParticleSystemSocket", "Active")
        self.width += 10
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Object" : "object"}
    def getOutputSocketNames(self):
        return {"Particle Systems" : "particleSystems",
                "Active" : "active"}

    def execute(self, object):
        if not object: return [], None
        particleSystems = object.particle_systems
        active = object.particle_systems.active
        return list(particleSystems), active
        

