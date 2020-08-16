import bpy
from .. utils.blender_ui import PieMenuHelper

class AlignPie(bpy.types.Menu, PieMenuHelper):
    bl_idname = "AN_MT_align_pie"
    bl_label = "Align Pie"

    @classmethod
    def poll(cls, context):
        tree = context.getActiveAnimationNodeTree()
        if tree is None: return False
        if tree.nodes.active is None: return False
        return True

    def drawLeft(self, layout):
        layout.operator("an.align_dependencies")

    def drawRight(self, layout):
        layout.operator("an.align_dependent_nodes")

    def drawTop(self, layout):
        layout.operator("an.align_top_selection_nodes")

    def drawBottom(self, layout):
        layout.operator("an.align_down_selection_nodes")
