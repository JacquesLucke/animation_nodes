import bpy
from ... base_types.node import AnimationNode

class ParticleInfo(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParticleInfo"
    bl_label = "Particle Info"

    def create(self):
        self.inputs.new("an_ParticleSocket", "Particle", "particle")
        self.outputs.new("an_VectorSocket", "Location", "location")
        self.outputs.new("an_VectorSocket", "Rotation", "rotation")
        self.outputs.new("an_FloatSocket", "Age", "age")
        self.outputs.new("an_VectorSocket", "Velocity", "velocity").hide = True
        self.outputs.new("an_VectorSocket", "Angular Velocity", "angularVelocity").hide = True
        self.outputs.new("an_FloatSocket", "Size", "size").hide = True
        self.outputs.new("an_StringSocket", "Alive State", "aliveState").hide = True
        self.outputs.new("an_BooleanSocket", "Is Exist", "isExist").hide = True
        self.outputs.new("an_BooleanSocket", "Is Visible", "isVisible").hide = True
        self.outputs.new("an_FloatSocket", "Lifetime", "lifetime").hide = True
        self.outputs.new("an_FloatSocket", "Birth Time", "birthTime").hide = True
        self.outputs.new("an_FloatSocket", "Die Time", "dieTime").hide = True
        self.outputs.new("an_VectorSocket", "Previous Location", "previousLocation").hide = True
        self.outputs.new("an_VectorSocket", "Previous Rotation", "previousRotation").hide = True
        self.outputs.new("an_VectorSocket", "Previous Velocity", "previousVelocity").hide = True
        self.outputs.new("an_VectorSocket", "Previous Angular Velocity", "previousAngularVelocity").hide = True

    def getExecutionCode(self, usedOutputs):
        lines = []

        lines.append("if particle:")
        if usedOutputs["Location"]: lines.append("    location = particle.location")
        if usedOutputs["Rotation"]: lines.append("    rotation = mathutils.Vector(particle.rotation.to_euler())")
        if usedOutputs["Velocity"]: lines.append("    velocity = particle.velocity")
        if usedOutputs["Angular Velocity"]: lines.append("    angularVelocity = particle.angular_velocity")
        if usedOutputs["Size"]: lines.append("    size = particle.size")
        if usedOutputs["Alive State"]: lines.append("    aliveState = particle.alive_state")
        if usedOutputs["Is Exist"]: lines.append("    isExist = particle.is_exist")
        if usedOutputs["Is Visible"]: lines.append("    isVisible = particle.is_visible")
        if usedOutputs["Lifetime"]: lines.append("    lifetime = particle.lifetime")
        if usedOutputs["Birth Time"]: lines.append("    birthTime = particle.birth_time")
        if usedOutputs["Die Time"]: lines.append("    dieTime = particle.die_time")
        if usedOutputs["Age"]: lines.append("    age = max(0, scene.frame_current - particle.birth_time)")
        if usedOutputs["Previous Location"]: lines.append("    previousLocation = particle.prev_location")
        if usedOutputs["Previous Rotation"]: lines.append("    previousRotation = mathutils.Vector(particle.prev_rotation.to_euler())")
        if usedOutputs["Previous Velocity"]: lines.append("    previousVelocity = particle.prev_velocity")
        if usedOutputs["Previous Angular Velocity"]: lines.append("    previousAngularVelocity = particle.prev_angular_velocity")
        lines.append("    pass")

        lines.append("else:")
        if usedOutputs["Location"]: lines.append("    location = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Rotation"]: lines.append("    rotation = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Velocity"]: lines.append("    velocity = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Angular Velocity"]: lines.append("    angularVelocity = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Size"]: lines.append("    size = 1")
        if usedOutputs["Alive State"]: lines.append("    aliveState = 'DEAD'")
        if usedOutputs["Is Exist"]: lines.append("    isExist = False")
        if usedOutputs["Is Visible"]: lines.append("    isVisible = False")
        if usedOutputs["Lifetime"]: lines.append("    lifetime = 0")
        if usedOutputs["Birth Time"]: lines.append("    birthTime = 0")
        if usedOutputs["Die Time"]: lines.append("    dieTime = 0")
        if usedOutputs["Age"]: lines.append("    age = 0")
        if usedOutputs["Previous Location"]: lines.append("    previousLocation = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Previous Rotation"]: lines.append("    previousRotation = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Previous Velocity"]: lines.append("    previousVelocity = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Previous Angular Velocity"]: lines.append("    previousAngularVelocity = mathutils.Vector((0, 0, 0))")
        lines.append("    pass")

        return lines

    def getModuleList(self):
        return ["mathutils"]
