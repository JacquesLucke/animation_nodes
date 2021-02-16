import bpy
import blf
from .. utils.selection import updateSelectionSorting

def drawCallback():
    fontID = 0
    blf.position(fontID, 15, 30, 0)
    blf.size(fontID, 20, 72)
    blf.draw(fontID, "Recording selection order. Press Esc to end.")


class RecordSelectionOrder(bpy.types.Operator):
    bl_idname = "an.record_selection_order"
    bl_label = "Record Selection Order"

    timer = None
    drawHandler = None

    def modal(self, context, event):
        if event.type == "ESC":
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            updateSelectionSorting(context.view_layer)

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        wm = context.window_manager
        self.timer = wm.event_timer_add(0.001, window = context.window)
        wm.modal_handler_add(self)

        self.drawHandler = bpy.types.SpaceView3D.draw_handler_add(drawCallback, (), 'WINDOW', 'POST_PIXEL')

        context.area.tag_redraw()

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self.timer)

        bpy.types.SpaceView3D.draw_handler_remove(self.drawHandler, 'WINDOW')

        context.area.tag_redraw()
