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

    def getExecutionCode(self):
        usedOutputs = self.getUsedOutputsDict()

        lines = []

        lines.append("if particle:")
        if usedOutputs["location"]: lines.append("    location = particle.location")
        if usedOutputs["rotation"]: lines.append("    rotation = mathutils.Vector(particle.rotation.to_euler())")
        if usedOutputs["velocity"]: lines.append("    velocity = particle.velocity")
        if usedOutputs["angularVelocity"]: lines.append("    angularVelocity = particle.angular_velocity")
        if usedOutputs["size"]: lines.append("    size = particle.size")
        if usedOutputs["aliveState"]: lines.append("    aliveState = particle.alive_state")
        if usedOutputs["isExist"]: lines.append("    isExist = particle.is_exist")
        if usedOutputs["isVisible"]: lines.append("    isVisible = particle.is_visible")
        if usedOutputs["lifetime"]: lines.append("    lifetime = particle.lifetime")
        if usedOutputs["birthTime"]: lines.append("    birthTime = particle.birth_time")
        if usedOutputs["dieTime"]: lines.append("    dieTime = particle.die_time")
        if usedOutputs["age"]: lines.append("    age = max(0, scene.frame_current - particle.birth_time)")
        if usedOutputs["previousLocation"]: lines.append("    previousLocation = particle.prev_location")
        if usedOutputs["previousRotation"]: lines.append("    previousRotation = mathutils.Vector(particle.prev_rotation.to_euler())")
        if usedOutputs["previousVelocity"]: lines.append("    previousVelocity = particle.prev_velocity")
        if usedOutputs["previousAngularVelocity"]: lines.append("    previousAngularVelocity = particle.prev_angular_velocity")
        lines.append("    pass")

        lines.append("else:")
        if usedOutputs["location"]: lines.append("    location = mathutils.Vector((0, 0, 0))")
        if usedOutputs["rotation"]: lines.append("    rotation = mathutils.Vector((0, 0, 0))")
        if usedOutputs["velocity"]: lines.append("    velocity = mathutils.Vector((0, 0, 0))")
        if usedOutputs["angularVelocity"]: lines.append("    angularVelocity = mathutils.Vector((0, 0, 0))")
        if usedOutputs["size"]: lines.append("    size = 1")
        if usedOutputs["aliveState"]: lines.append("    aliveState = 'DEAD'")
        if usedOutputs["isExist"]: lines.append("    isExist = False")
        if usedOutputs["isVisible"]: lines.append("    isVisible = False")
        if usedOutputs["lifetime"]: lines.append("    lifetime = 0")
        if usedOutputs["birthTime"]: lines.append("    birthTime = 0")
        if usedOutputs["dieTime"]: lines.append("    dieTime = 0")
        if usedOutputs["age"]: lines.append("    age = 0")
        if usedOutputs["previousLocation"]: lines.append("    previousLocation = mathutils.Vector((0, 0, 0))")
        if usedOutputs["previousRotation"]: lines.append("    previousRotation = mathutils.Vector((0, 0, 0))")
        if usedOutputs["previousVelocity"]: lines.append("    previousVelocity = mathutils.Vector((0, 0, 0))")
        if usedOutputs["previousAngularVelocity"]: lines.append("    previousAngularVelocity = mathutils.Vector((0, 0, 0))")
        lines.append("    pass")

        return lines

    def getModuleList(self):
        return ["mathutils"]
