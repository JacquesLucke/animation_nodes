import bpy
from .. draw_handler import drawHandler
from .. preferences import getMeshIndicesSettings
from .. graphics.mesh_indices import drawVertexIndices_ObjectMode

@drawHandler("SpaceView3D", "WINDOW")
def drawIndicesOfSelectedObjects():
    prefs = getMeshIndicesSettings()
    if not prefs.activated:
        return
    for object in bpy.context.selected_objects:
        if object.type == "MESH" and object.mode == "OBJECT":
            drawVertexIndices_ObjectMode(object,
                color = prefs.textColor,
                fontSize = prefs.fontSize)

def drawPanel(self, context):
    if context.mode != "OBJECT":
        return

    prefs = getMeshIndicesSettings()
    row = self.layout.row()
    row.prop(prefs, "activated", text = "Vertex Indices")
    subRow = row.row()
    subRow.active = prefs.activated
    subRow.prop(prefs, "textColor", text = "")

def register():
    bpy.types.VIEW3D_PT_view3d_display.append(drawPanel)

def unregister():
    bpy.types.VIEW3D_PT_view3d_display.remove(drawPanel)
