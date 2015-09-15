import bpy
from . nodes.animation.debug_interpolation import drawInterpolationPreviews

def drawNodeEditor():
    drawInterpolationPreviews()

_nodeDrawHandler = None
def register():
    global _nodeDrawHandler
    _nodeDrawHandler = bpy.types.SpaceNodeEditor.draw_handler_add(drawNodeEditor, (), "WINDOW", "POST_PIXEL")

def unregister():
    bpy.types.SpaceNodeEditor.draw_handler_remove(_nodeDrawHandler, "WINDOW")
