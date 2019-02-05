import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode, VectorizedSocket

noBaseMatMessage = "No Base Material"
noInstMatMessage = "No Prefix Name"


class MaterialInstancerNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MaterialInstancerNode"
    bl_label = "Material Instancer"

    errorMessage = StringProperty()
    myLabel = StringProperty()

    useList = VectorizedSocket.newProperty()

    i_mat_bool = BoolProperty(name="Instance Material",
                              default=False, update=propertyChanged)
    rm_mat_bool = BoolProperty(
        name="Remove Materials", default=False, update=propertyChanged)

    def create(self):
        self.newInput("Text", "Base Material Name", "b_mat")
        self.newInput("Text", "Prefix For Instance Materials", "i_mat")
        self.newInput("Integer", "Amount", "nmat")

    def draw(self, layout):
        layout.prop(self, "i_mat_bool")
        layout.prop(self, "rm_mat_bool")
        if self.errorMessage != "":
            layout.label(self.errorMessage, icon="ERROR")

    def execute(self, b_mat, i_mat, nmat):
        self.errorMessage = ""

        #Error messages
        if b_mat is "":
            self.errorMessage = noBaseMatMessage
            return

        #Materials remover except "the base material"
        if self.rm_mat_bool:
            if len(bpy.data.materials) >= 1:
                for material in bpy.data.materials:
                    if material.name != b_mat:
                        #material.user_clear()
                        bpy.data.materials.remove(material)
            else:
                return

        #Error message
        if i_mat is "":
            self.errorMessage = noInstMatMessage
            return

        #Material instancer
        if self.i_mat_bool:
            for i in range(nmat):
                if i <= 9:
                    imat = i_mat + '.00' + str(i)
                elif i > 9 and i <= 99:
                    imat = i_mat + '.0' + str(i)
                elif i > 99:
                    imat = i_mat + '.' + str(i)

                if imat not in bpy.data.materials:
                    mat = bpy.data.materials[b_mat].copy()
                    mat.name = imat
