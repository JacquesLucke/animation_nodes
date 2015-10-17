import bpy
import itertools
from .. utils.timing import prettyTime
from .. utils.nodes import getAnimationNodeTrees

class OverviewPanel(bpy.types.Panel):
    bl_idname = "an_overview_panel"
    bl_label = "Overview"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Animation Nodes"

    def draw(self, context):
        layout = self.layout

        trees = getAnimationNodeTrees()

        col = layout.box().column(align = True)
        for tree in trees:
            row = col.row(align = True)
            row.label(tree.name)
            row.label(prettyTime(tree.executionTime), icon = "TIME")

            icon = "LAYER_ACTIVE" if tree.autoExecution.enabled else "LAYER_USED"
            row.prop(tree.autoExecution, "enabled", icon = icon, text = "", icon_only = True)

        nodes = [node for node in tree.nodes for tree in trees]
        totalNodes = len(nodes)
        layout.label("Total Nodes: {}".format(totalNodes))
