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
        layout.operator("an.align_dependencies", text = "Dependencies", icon = "ANCHOR_RIGHT")

    def drawRight(self, layout):
        layout.operator("an.align_dependent_nodes", text = "Dependent", icon = "ANCHOR_LEFT")

    def drawTop(self, layout):
        layout.operator("an.stake_up_selection_nodes", text = "Selection", icon = "ANCHOR_BOTTOM")

    def drawBottom(self, layout):
        layout.operator("an.stake_down_selection_nodes", text = "Selection", icon = "ANCHOR_TOP")

    def drawTopLeft(self, layout):
        layout.operator("an.align_top_selection_nodes", text = "Selection", icon = "TRIA_UP_BAR")

    def drawTopRight(self, layout):
        layout.operator("an.align_top_selection_nodes", text = "Selection", icon = "TRIA_UP_BAR")

    def drawBottomLeft(self, layout):
        layout.operator("an.align_left_side_selection_nodes", text = "Selection", icon = "TRIA_LEFT_BAR")

    def drawBottomRight(self, layout):
        layout.operator("an.align_right_side_selection_nodes", text = "Selection", icon = "TRIA_RIGHT_BAR")
