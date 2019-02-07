import bpy
from bpy.props import *
from ... base_types import AnimationNode

noMatMessage = "No Material Name"
noShaderMessage = "No Shader Node Name"
noShaderProMessage = "No Property Name"
noShdMessage = "Material does not has this Shader Node Name"
noProMessage = "Shader does not has this Property Name"
noValEListMessage = "Empty Value list"

class ShaderNodeController(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShaderNodeController"
    bl_label = "Shader Node Controller"
    bl_width_default = 180

    errorMessage: StringProperty()
    message1: StringProperty()

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(text = self.errorMessage, icon="ERROR")
        if (self.message1 != ""):
            layout.label(text = self.message1, icon="INFO")

    def create(self):
        self.newInput("Material List", "Materials", "mat")
        self.newInput("Text", "Shader Node Name", "shd")
        self.newInput("Text", "Shader Property Name", "shd_pro_nam")
        self.newInput("Generic List", "Values", "val")

    def execute(self, mat, shd, shd_pro_nam, val):
        self.errorMessage = ""

        #Error messages
        if len(mat) < 1 or mat[0] is None:
            self.errorMessage = noMatMessage
            return

        if shd is "":
            self.errorMessage = noShaderMessage
            return

        if shd_pro_nam is "":
            self.errorMessage = noShaderProMessage
            return
        
        if len(mat) >= 1:
            for mati in mat:
                if mati is not None:
                    if shd not in bpy.data.materials[mati.name].node_tree.nodes:
                        self.errorMessage = noShdMessage
                        return

            for mati in mat:
                if mati is not None:
                    if shd_pro_nam not in bpy.data.materials[mati.name].node_tree.nodes[shd].inputs:
                        self.errorMessage = noProMessage
                        return

        #Information for shader property inputs
        provals = bpy.data.materials[mat[0].name].node_tree.nodes[shd].inputs[shd_pro_nam].default_value
        try:
            self.message1 = shd_pro_nam + " Property" + " has " + str(len(provals)) + " inputs"
        except:
            self.message1 = shd_pro_nam + " Property" + " has " + str(1) + " input"

        if len(val) < 1:
            self.errorMessage = noValEListMessage
            return
        
        #Shader property controler
        #Each material's shader node has its own value
        if len(val) >= 1 and len(val) == len(mat):
            i = 0
            for mati in mat:
                if mati is not None:
                    vali = val[i]
                    bpy.data.materials[mati.name].node_tree.nodes[shd].inputs[shd_pro_nam].default_value = vali
                    i = i + 1
        #One value for all meterial's shader node            
        elif len(val) >= 1 and len(val) != len(mat):
            for mati in mat:
                if mati is not None:
                    bpy.data.materials[mati.name].node_tree.nodes[shd].inputs[shd_pro_nam].default_value = val[0]
