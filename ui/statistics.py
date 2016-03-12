import bpy
from collections import defaultdict
from .. utils.nodes import getAnimationNodeTrees
from .. graphics.drawing_2d import draw_text

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

        for tree in getAnimationNodeTrees():
            NodeTreeInfo(tree)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == "LEFTMOUSE":
            return self.finish()

        if event.type in {"RIGHTMOUSE", "ESC"}:
            return self.finish()

        return {"RUNNING_MODAL"}

    def finish(self):
        bpy.types.SpaceNodeEditor.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def draw_callback_px(self):
        draw_text("Hello World", 200, 200)

class NodeTreeInfo:

    def __init__(self, nodeTree):
        self.typeCounter = defaultdict(int)
        for node in nodeTree.nodes:
            self.typeCounter[node.bl_idname] += 1

        self.totalNodeAmount = len(nodeTree.nodes)
        self.totalLinkAmount = len(nodeTree.links)

        self.anNodesAmount = self.totalNodeAmount \
                             - self.typeCounter["NodeReroute"] \
                             - self.typeCounter["NodeFrame"]

        print(self.totalNodeAmount)
        print(self.totalLinkAmount)
        print(self.anNodesAmount)
        print()
