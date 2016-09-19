import bpy
from ... base_types import AnimationNode

class ParticleInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ParticleInfoNode"
    bl_label = "Particle Info"

    def create(self):
        self.newInput("Particle", "Particle", "particle")

        self.newOutput("Vector", "Location", "location")
        self.newOutput("Euler", "Rotation", "rotation")
        self.newOutput("Vector", "Velocity", "velocity", hide = True)
        self.newOutput("Euler", "Angular Velocity", "angularVelocity", hide = True)
        self.newOutput("Float", "Size", "size", hide = True)
        self.newOutput("Text", "Alive State", "aliveState", hide = True)
        self.newOutput("Boolean", "Is Exist", "isExist", hide = True)
        self.newOutput("Boolean", "Is Visible", "isVisible", hide = True)
        self.newOutput("Float", "Lifetime", "lifetime", hide = True)
        self.newOutput("Float", "Birth Time", "birthTime", hide = True)
        self.newOutput("Float", "Die Time", "dieTime", hide = True)
        self.newOutput("Vector", "Previous Location", "previousLocation", hide = True)
        self.newOutput("Euler", "Previous Rotation", "previousRotation", hide = True)
        self.newOutput("Vector", "Previous Velocity", "previousVelocity", hide = True)
        self.newOutput("Euler", "Previous Angular Velocity", "previousAngularVelocity", hide = True)
        self.newOutput("Float List", "Hair Time", "hairTime", hide = True)
        self.newOutput("Float List", "Hair Weight", "hairWeight", hide = True)
        self.newOutput("Vector List", "Hair Points", "hairPoints", hide = True)
        self.newOutput("Vector List", "Hair Points Local", "hairPointsLocal", hide = True)

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()

        lines = []

        lines.append("if particle:")
        if isLinked["location"]: lines.append("    location = particle.location")
        if isLinked["rotation"]: lines.append("    rotation = particle.rotation.to_euler()")
        if isLinked["velocity"]: lines.append("    velocity = particle.velocity")
        if isLinked["angularVelocity"]: lines.append("    angularVelocity = Euler(particle.angular_velocity)")
        if isLinked["size"]: lines.append("    size = particle.size")
        if isLinked["aliveState"]: lines.append("    aliveState = particle.alive_state")
        if isLinked["isExist"]: lines.append("    isExist = particle.is_exist")
        if isLinked["isVisible"]: lines.append("    isVisible = particle.is_visible")
        if isLinked["lifetime"]: lines.append("    lifetime = particle.lifetime")
        if isLinked["birthTime"]: lines.append("    birthTime = particle.birth_time")
        if isLinked["dieTime"]: lines.append("    dieTime = particle.die_time")
        if isLinked["previousLocation"]: lines.append("    previousLocation = particle.prev_location")
        if isLinked["previousRotation"]: lines.append("    previousRotation = particle.prev_rotation.to_euler()")
        if isLinked["previousVelocity"]: lines.append("    previousVelocity = particle.prev_velocity")
        if isLinked["previousAngularVelocity"]: lines.append("    previousAngularVelocity = Euler(particle.prev_angular_velocity)")

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
        if isLinked["location"]: lines.append("    location = Vector((0, 0, 0))")
        if isLinked["rotation"]: lines.append("    rotation = Euler((0, 0, 0))")
        if isLinked["velocity"]: lines.append("    velocity = Vector((0, 0, 0))")
        if isLinked["angularVelocity"]: lines.append("    angularVelocity = Euler((0, 0, 0))")
        if isLinked["size"]: lines.append("    size = 1")
        if isLinked["aliveState"]: lines.append("    aliveState = 'DEAD'")
        if isLinked["isExist"]: lines.append("    isExist = False")
        if isLinked["isVisible"]: lines.append("    isVisible = False")
        if isLinked["lifetime"]: lines.append("    lifetime = 0")
        if isLinked["birthTime"]: lines.append("    birthTime = 0")
        if isLinked["dieTime"]: lines.append("    dieTime = 0")
        if isLinked["previousLocation"]: lines.append("    previousLocation = Vector((0, 0, 0))")
        if isLinked["previousRotation"]: lines.append("    previousRotation = Euler((0, 0, 0))")
        if isLinked["previousVelocity"]: lines.append("    previousVelocity = Vector((0, 0, 0))")
        if isLinked["previousAngularVelocity"]: lines.append("    previousAngularVelocity = Euler((0, 0, 0))")

        if isLinked["hairTime"]:        lines.append("    hairTime = []")
        if isLinked["hairWeight"]:      lines.append("    hairWeight = []")
        if isLinked["hairPoints"]:      lines.append("    hairPoints = []")
        if isLinked["hairPointsLocal"]: lines.append("    hairPointsLocal = []")
        lines.append("    pass")

        return lines
