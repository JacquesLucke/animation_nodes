import bpy
from .. utils.timing import prettyTime
from .. draw_handler import drawHandler
from .. graphics.drawing_2d import drawText
from .. utils.blender_ui import getDpiFactor

@drawHandler("SpaceNodeEditor", "WINDOW")
def drawNodeEditorHud():
    tree = bpy.context.getActiveAnimationNodeTree()
    if tree is None:
        return

    dpiFactor = getDpiFactor()

    top = bpy.context.region.height

    executionTime = prettyTime(tree.lastExecutionInfo.executionTime)
    drawText(executionTime, 10 * dpiFactor, top - 20 * dpiFactor,
        size = 11, color = (1, 1, 1, 0.5))
