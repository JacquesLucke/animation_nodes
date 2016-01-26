import bpy
from ... base_types.node import AnimationNode

class ParticleInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParticleInfoNode"
    bl_label = "Particle Info"

    def create(self):
        self.inputs.new("an_ParticleSocket", "Particle", "particle")
        self.outputs.new("an_VectorSocket", "Location", "location")
        self.outputs.new("an_VectorSocket", "Rotation", "rotation")
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
        
        self.outputs.new("an_FloatListSocket", "Hair Time", "hairTime").hide = True
        self.outputs.new("an_FloatListSocket", "Hair Weight", "hairWeight").hide = True
        self.outputs.new("an_VectorListSocket", "Hair Points", "hairPoints").hide = True
        self.outputs.new("an_VectorListSocket", "Hair Points Local", "hairPointsLocal").hide = True

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()

        lines = []

        lines.append("if particle:")
        if isLinked["location"]: lines.append("    location = particle.location")
        if isLinked["rotation"]: lines.append("    rotation = mathutils.Vector(particle.rotation.to_euler())")
        if isLinked["velocity"]: lines.append("    velocity = particle.velocity")
        if isLinked["angularVelocity"]: lines.append("    angularVelocity = particle.angular_velocity")
        if isLinked["size"]: lines.append("    size = particle.size")
        if isLinked["aliveState"]: lines.append("    aliveState = particle.alive_state")
        if isLinked["isExist"]: lines.append("    isExist = particle.is_exist")
        if isLinked["isVisible"]: lines.append("    isVisible = particle.is_visible")
        if isLinked["lifetime"]: lines.append("    lifetime = particle.lifetime")
        if isLinked["birthTime"]: lines.append("    birthTime = particle.birth_time")
        if isLinked["dieTime"]: lines.append("    dieTime = particle.die_time")
        if isLinked["previousLocation"]: lines.append("    previousLocation = particle.prev_location")
        if isLinked["previousRotation"]: lines.append("    previousRotation = mathutils.Vector(particle.prev_rotation.to_euler())")
        if isLinked["previousVelocity"]: lines.append("    previousVelocity = particle.prev_velocity")
        if isLinked["previousAngularVelocity"]: lines.append("    previousAngularVelocity = particle.prev_angular_velocity")
        
        hair = ["hairTime", "hairWeight", "hairPoints", "hairPointsLocal"]
        if any([isLinked[item] for item in hair]):
            lines.append("    " + ", ".join(hair) + " = [], [], [] ,[]")
            lines.append("    if particle.hair_keys:")
            lines.append(" " * 8 + "for key in particle.hair_keys:")
            if isLinked["hairTime"]:        lines.append(" " * 12 + "hairTime.append(key.time)")
            if isLinked["hairWeight"]:      lines.append(" " * 12 + "hairWeight.append(key.weight)")
            if isLinked["hairPoints"]:      lines.append(" " * 12 + "hairPoints.append(key.co)")
            if isLinked["hairPointsLocal"]: lines.append(" " * 12 + "hairPointsLocal.append(key.co_local)")
            
        lines.append("    pass")

        lines.append("else:")
        if isLinked["location"]: lines.append("    location = mathutils.Vector((0, 0, 0))")
        if isLinked["rotation"]: lines.append("    rotation = mathutils.Vector((0, 0, 0))")
        if isLinked["velocity"]: lines.append("    velocity = mathutils.Vector((0, 0, 0))")
        if isLinked["angularVelocity"]: lines.append("    angularVelocity = mathutils.Vector((0, 0, 0))")
        if isLinked["size"]: lines.append("    size = 1")
        if isLinked["aliveState"]: lines.append("    aliveState = 'DEAD'")
        if isLinked["isExist"]: lines.append("    isExist = False")
        if isLinked["isVisible"]: lines.append("    isVisible = False")
        if isLinked["lifetime"]: lines.append("    lifetime = 0")
        if isLinked["birthTime"]: lines.append("    birthTime = 0")
        if isLinked["dieTime"]: lines.append("    dieTime = 0")
        if isLinked["previousLocation"]: lines.append("    previousLocation = mathutils.Vector((0, 0, 0))")
        if isLinked["previousRotation"]: lines.append("    previousRotation = mathutils.Vector((0, 0, 0))")
        if isLinked["previousVelocity"]: lines.append("    previousVelocity = mathutils.Vector((0, 0, 0))")
        if isLinked["previousAngularVelocity"]: lines.append("    previousAngularVelocity = mathutils.Vector((0, 0, 0))")
        
        if isLinked["hairTime"]:        lines.append("    hairTime = []")
        if isLinked["hairWeight"]:      lines.append("    hairWeight = []")
        if isLinked["hairPoints"]:      lines.append("    hairPoints = []")
        if isLinked["hairPointsLocal"]: lines.append("    hairPointsLocal = []")
        lines.append("    pass")

        return lines

    def getUsedModules(self):
        return ["mathutils"]
