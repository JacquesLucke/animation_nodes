import bpy
from .. utils.timing import prettyTime
from .. draw_handler import drawHandler
from .. utils.blender_ui import getDpi, getDpiFactor
from .. graphics.drawing_2d import drawText, setTextDrawingDpi

@drawHandler("SpaceNodeEditor", "WINDOW")
def drawNodeEditorHud():
    tree = bpy.context.getActiveAnimationNodeTree()
    if tree is None:
        return

    setTextDrawingDpi(getDpi())
    dpiFactor = getDpiFactor()

    for region in bpy.context.area.regions:
        if region.type == "WINDOW":
            windowRegion = region
        elif region.type == "TOOLS":
            toolsRegion = region

    top = windowRegion.height
    left = toolsRegion.width

    executionTime = prettyTime(tree.lastExecutionInfo.executionTime)
    drawText(executionTime, left + 10 * dpiFactor, top - 20 * dpiFactor,
        size = 11, color = (1, 1, 1, 0.5))
