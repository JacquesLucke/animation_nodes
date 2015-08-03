import bpy
from ... base_types.node import AnimationNode


class ParticleInfo(bpy.types.Node, AnimationNode):
    bl_idname = "mn_ParticleInfo"
    bl_label = "Particle Info"

    inputNames = { "Particle" : "particle" }
    outputNames = { "Location" : "location",
                    "Rotation" : "rotation",
                    "Age" : "age",
                    "Velocity" : "velocity",
                    "Angular Velocity" : "angularVelocity",
                    "Size" : "size",
                    "Alive State" : "aliveState",
                    "Is Exist" : "isExist",
                    "Is Visible" : "isVisible",
                    "Lifetime" : "lifetime",
                    "Birth Time" : "birthTime",
                    "Die Time" : "dieTime",
                    "Previous Location" : "previousLocation",
                    "Previous Rotation" : "previousRotation",
                    "Previous Velocity" : "previousVelocity",
                    "Previous Angular Velocity" : "previousAngularVelocity" }

    def create(self):
        self.inputs.new("mn_ParticleSocket", "Particle")
        self.outputs.new("mn_VectorSocket", "Location")
        self.outputs.new("mn_VectorSocket", "Rotation")
        self.outputs.new("mn_FloatSocket", "Age")
        self.outputs.new("mn_VectorSocket", "Velocity").hide = True
        self.outputs.new("mn_VectorSocket", "Angular Velocity").hide = True
        self.outputs.new("mn_FloatSocket", "Size").hide = True
        self.outputs.new("mn_StringSocket", "Alive State").hide = True
        self.outputs.new("mn_BooleanSocket", "Is Exist").hide = True
        self.outputs.new("mn_BooleanSocket", "Is Visible").hide = True
        self.outputs.new("mn_FloatSocket", "Lifetime").hide = True
        self.outputs.new("mn_FloatSocket", "Birth Time").hide = True
        self.outputs.new("mn_FloatSocket", "Die Time").hide = True
        self.outputs.new("mn_VectorSocket", "Previous Location").hide = True
        self.outputs.new("mn_VectorSocket", "Previous Rotation").hide = True
        self.outputs.new("mn_VectorSocket", "Previous Velocity").hide = True
        self.outputs.new("mn_VectorSocket", "Previous Angular Velocity").hide = True

    def getExecutionCode(self, usedOutputs):
        codeLines = []

        codeLines.append("if %particle%:")
        if usedOutputs["Location"]: codeLines.append("    $location$ = %particle%.location")
        if usedOutputs["Rotation"]: codeLines.append("    $rotation$ = mathutils.Vector(%particle%.rotation.to_euler())")
        if usedOutputs["Velocity"]: codeLines.append("    $velocity$ = %particle%.velocity")
        if usedOutputs["Angular Velocity"]: codeLines.append("    $angularVelocity$ = %particle%.angular_velocity")
        if usedOutputs["Size"]: codeLines.append("    $size$ = %particle%.size")
        if usedOutputs["Alive State"]: codeLines.append("    $aliveState$ = %particle%.alive_state")
        if usedOutputs["Is Exist"]: codeLines.append("    $isExist$ = %particle%.is_exist")
        if usedOutputs["Is Visible"]: codeLines.append("    $isVisible$ = %particle%.is_visible")
        if usedOutputs["Lifetime"]: codeLines.append("    $lifetime$ = %particle%.lifetime")
        if usedOutputs["Birth Time"]: codeLines.append("    $birthTime$ = %particle%.birth_time")
        if usedOutputs["Die Time"]: codeLines.append("    $dieTime$ = %particle%.die_time")
        if usedOutputs["Age"]: codeLines.append("    $age$ = max(0, scene.frame_current - %particle%.birth_time)")
        if usedOutputs["Previous Location"]: codeLines.append("    $previousLocation$ = %particle%.prev_location")
        if usedOutputs["Previous Rotation"]: codeLines.append("    $previousRotation$ = mathutils.Vector(%particle%.prev_rotation.to_euler())")
        if usedOutputs["Previous Velocity"]: codeLines.append("    $previousVelocity$ = %particle%.prev_velocity")
        if usedOutputs["Previous Angular Velocity"]: codeLines.append("    $previousAngularVelocity$ = %particle%.prev_angular_velocity")
        codeLines.append("    pass")

        codeLines.append("else:")
        if usedOutputs["Location"]: codeLines.append("    $location$ = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Rotation"]: codeLines.append("    $rotation$ = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Velocity"]: codeLines.append("    $velocity$ = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Angular Velocity"]: codeLines.append("    $angularVelocity$ = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Size"]: codeLines.append("    $size$ = 1")
        if usedOutputs["Alive State"]: codeLines.append("    $aliveState$ = 'DEAD'")
        if usedOutputs["Is Exist"]: codeLines.append("    $isExist$ = False")
        if usedOutputs["Is Visible"]: codeLines.append("    $isVisible$ = False")
        if usedOutputs["Lifetime"]: codeLines.append("    $lifetime$ = 0")
        if usedOutputs["Birth Time"]: codeLines.append("    $birthTime$ = 0")
        if usedOutputs["Die Time"]: codeLines.append("    $dieTime$ = 0")
        if usedOutputs["Age"]: codeLines.append("    $age$ = 0")
        if usedOutputs["Previous Location"]: codeLines.append("    $previousLocation$ = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Previous Rotation"]: codeLines.append("    $previousRotation$ = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Previous Velocity"]: codeLines.append("    $previousVelocity$ = mathutils.Vector((0, 0, 0))")
        if usedOutputs["Previous Angular Velocity"]: codeLines.append("    $previousAngularVelocity$ = mathutils.Vector((0, 0, 0))")
        codeLines.append("    pass")

        return "\n".join(codeLines)

    def getModuleList(self):
        return ["mathutils"]
