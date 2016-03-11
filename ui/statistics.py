import bpy
from mathutils import Vector
from collections import defaultdict
from .. utils.nodes import getAnimationNodeTrees
from .. graphics.drawing_2d import draw_text, set_text_drawing_dpi, draw_horizontal_line, draw_vertical_line
from .. graphics.rectangle import Rectangle
from .. utils.blender_ui import getDpiFactor, getDpi

class StatisticsDrawer(bpy.types.Operator):
    bl_idname = "an.statistics_drawer"
    bl_label = "Statistics Drawer"

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR"

    def invoke(self, context, event):
        args = ()
        self.draw_handler = bpy.types.SpaceNodeEditor.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)

        self.stats = NodeStatistics(getAnimationNodeTrees())
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {"RIGHTMOUSE", "ESC"}:
            return self.finish()

        return {"PASS_THROUGH"}

    def finish(self):
        bpy.types.SpaceNodeEditor.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def draw_callback_px(self):
        region = bpy.context.region

        dpiFactor = getDpiFactor()
        bg = Rectangle.fromRegionDimensions(region)
        bg.color = (1, 1, 1, 0.5)
        bg.draw()

        set_text_drawing_dpi(getDpi())

        draw_text("Press ESC to exit this view", 10 * dpiFactor, region.height - 20 * dpiFactor,
            color = (0, 0, 0, 0.5), size = 11)

        offset = Vector((150 * dpiFactor, region.height - 100 * dpiFactor))

        for i in range(4):
            draw_vertical_line((150 + 100 * i) * dpiFactor, region.height - 100 * dpiFactor, -200 * dpiFactor,
                width = 1, color = (0, 0, 0, 0.5))

        for i in range(self.stats.nodeTreeAmount):
            draw_horizontal_line


class NodeStatistics:
    def __init__(self, nodeTrees):
        self.nodeTreeAmount = len(nodeTrees)
        self.nodeTreeStats = [TreeStatistics.fromTree(tree) for tree in nodeTrees]
        self.combinedStats = TreeStatistics.fromMerge(self.nodeTreeStats)

class TreeStatistics:
    def __init__(self):
        self.name = ""
        self.totalNodeAmount = 0
        self.totalLinkAmount = 0
        self.functionalNodeAmount = 0
        self.subprogramAmount = 0
        self.amountByIdName = defaultdict(int)

    @classmethod
    def fromTree(cls, nodeTree):
        stats = cls()

        stats.name = nodeTree.name
        stats.totalNodeAmount = len(nodeTree.nodes)
        stats.totalLinkAmount = len(nodeTree.links)
        stats.subprogramAmount = len(nodeTree.subprogramNetworks)

        for node in nodeTree.nodes:
            stats.amountByIdName[node.bl_idname] += 1

        stats.functionalNodeAmount = stats.totalLinkAmount \
                     - stats.amountByIdName["NodeReroute"] \
                     - stats.amountByIdName["NodeFrame"]

        return stats

    @classmethod
    def fromMerge(cls, statistics):
        stats = cls()

        stats.name = ", ".join(s.name for s in statistics)
        stats.totalNodeAmount = sum(s.totalNodeAmount for s in statistics)
        stats.totalLinkAmount = sum(s.totalLinkAmount for s in statistics)
        stats.functionalNodeAmount = sum(s.functionalNodeAmount for s in statistics)
        stats.subprogramAmount = sum(s.subprogramAmount for s in statistics)

        for s in statistics:
            for idName, amount in s.amountByIdName.items():
                stats.amountByIdName[idName] += amount

        return stats
