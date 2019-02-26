import bpy
from bpy.props import *
from ... base_types import AnimationNode, VectorizedSocket

noShdMessage = "Material does not has this Shader Node Name"
noProMessage = "Shader does not has this Property Name"

class ShaderNodeController(bpy.types.Node, AnimationNode):
    bl_idname = "an_ShaderNodeController"
    bl_label = "Shader Node Controller"
    bl_width_default = 180

    useMaterialList: VectorizedSocket.newProperty()
    useGenericList: VectorizedSocket.newProperty()

    errorMessage: StringProperty()
    messageInfo: StringProperty()

    def draw(self, layout):
        if self.errorMessage != "":
            layout.label(text = self.errorMessage, icon="ERROR")
        if (self.messageInfo != ""):
            layout.label(text = self.messageInfo, icon="INFO")

    def create(self):
        self.newInput(VectorizedSocket("Material", "useMaterialList",
             ("Material", "mat"), ("Materials", "mats")))
        self.newInput("Text", "Shader Node", "shader")
        self.newInput("Text", "Shader Property", "shader_pro")
        self.newInput(VectorizedSocket("Generic", "useGenericList",
             ("Value", "value"), ("Values", "values")))
        self.newOutput(VectorizedSocket("Generic", "useGenericList",
             ("For Extra Property", "forExtraProperty"), ("For Extra Property", "forExtraPropertys")))     
        visibleOutputs = ("")
        for socket in self.outputs:
            socket.hide = socket.name not in visibleOutputs

    def getExecutionFunctionName(self):
        if self.useMaterialList:
            return "executeList"                   
        else:
            return "executeSingle"
            
    def executeSingle(self, mat, shader, shader_pro, value):
        self.errorMessage = ""
        if mat is None: return
        forExtraProperty = bpy.data.materials[mat.name].node_tree    
        if shader is "": return forExtraProperty
        if shader not in bpy.data.materials[mat.name].node_tree.nodes:
            self.errorMessage = noShdMessage
            return forExtraProperty
        if shader_pro is "": return forExtraProperty
        if shader_pro not in bpy.data.materials[mat.name].node_tree.nodes[shader].inputs:
            self.errorMessage = noProMessage
            return forExtraProperty
        pro_input = bpy.data.materials[mat.name].node_tree.nodes[shader].inputs[shader_pro].default_value 
        try:
            self.messageInfo = shader_pro + " Property" + " has " + str(len(pro_input)) + " inputs"
        except:
            self.messageInfo = shader_pro + " Property" + " has " + str(1) + " input"
        if value is None: return forExtraProperty
        bpy.data.materials[mat.name].node_tree.nodes[shader].inputs[shader_pro].default_value = value  
        return forExtraProperty
        
    def executeList(self, mats, shader, shader_pro, values):
        self.errorMessage = ""
        if mats is None or len(mats) < 1: return
        forExtraPropertys = []
        for i in range(len(mats)):
            if mats[i] is None: return
            forExtraPropertys.append(bpy.data.materials[mats[i].name].node_tree)
        if shader is "": return forExtraPropertys
        if shader not in bpy.data.materials[mats[0].name].node_tree.nodes:
            self.errorMessage = noShdMessage
            return forExtraPropertys
        if shader_pro is "": return forExtraPropertys
        if shader_pro not in bpy.data.materials[mats[0].name].node_tree.nodes[shader].inputs:
            self.errorMessage = noProMessage
            return forExtraPropertys
        pro_input = bpy.data.materials[mats[0].name].node_tree.nodes[shader].inputs[shader_pro].default_value 
        try:
            self.messageInfo = shader_pro + " Property" + " has " + str(len(pro_input)) + " inputs"
        except:
            self.messageInfo = shader_pro + " Property" + " has " + str(1) + " input"
        if values is None or len(values) < 1: return forExtraPropertys
        for i in range(len(mats)):
            if mats[i] is None: return
            if i < len(values):
                valuei = values[i]
            else:
                valuei = values[-1]         
            bpy.data.materials[mats[i].name].node_tree.nodes[shader].inputs[shader_pro].default_value = valuei
        return forExtraPropertys    
            
