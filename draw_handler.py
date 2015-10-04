import bpy
from . nodes.generic.debug_drawer import drawDebugTextBoxes
from . nodes.interpolation.debug import drawInterpolationPreviews

def drawNodeEditor():
    drawDebugTextBoxes()
    drawInterpolationPreviews()

_nodeDrawHandler = None
def register():
    global _nodeDrawHandler
    _nodeDrawHandler = bpy.types.SpaceNodeEditor.draw_handler_add(drawNodeEditor, (), "WINDOW", "POST_PIXEL")

def unregister():
    bpy.types.SpaceNodeEditor.draw_handler_remove(_nodeDrawHandler, "WINDOW")
