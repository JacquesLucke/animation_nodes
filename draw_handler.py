import bpy
from . preferences import getExecutionCodeType
from . ui.node_editor_hud import drawNodeEditorHud
from . execution.measurements import drawMeasurementResults
from . nodes.generic.debug_drawer import drawDebugTextBoxes
from . nodes.interpolation.debug import drawInterpolationPreviews

def drawNodeEditor():
    drawDebugTextBoxes()
    drawInterpolationPreviews()
    if getExecutionCodeType() == "MEASURE":
        drawMeasurementResults()
    drawNodeEditorHud()

_nodeDrawHandler = None
def register():
    global _nodeDrawHandler
    _nodeDrawHandler = bpy.types.SpaceNodeEditor.draw_handler_add(drawNodeEditor, (), "WINDOW", "POST_PIXEL")

def unregister():
    bpy.types.SpaceNodeEditor.draw_handler_remove(_nodeDrawHandler, "WINDOW")
