import blf
import bpy
from mathutils import Vector
from bpy_extras import view3d_utils
from bpy.props import *

def getIDKeyIntegerName(name):
    IDKeyName="AN*Integer*%s" % name
    return IDKeyName

def getCenter(object):
    local_bbox_center = 0.125 * sum((Vector(b) for b in object.bound_box), Vector())
    global_bbox_center = object.matrix_world @ local_bbox_center
    return global_bbox_center

def get2DPosition(point, context):
    region=context.region
    rv3d=context.space_data.region_3d
    coord=view3d_utils.location_3d_to_region_2d(region, rv3d, point, default=None)
    return coord

def get3DAreas():
    area_list=[]
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type=="VIEW_3D": area_list.append(area)
    return area_list

def getObjectWithIDKeys(idkey, onlyselected):
    obj_list=[]
    if onlyselected: objects=bpy.context.selected_objects
    else: objects=bpy.context.scene.objects
    for obj in objects:
        try:
            obj[idkey]
            obj_list.append(obj)
        except KeyError: pass
    return obj_list
                
def draw_callback_px(self, context):
    font_id=0
    blf.enable(font_id , blf.SHADOW )
    blf.shadow(font_id, 5,0.0,0.0,0.0,1)
    blf.shadow_offset(font_id, 1, -1)

    blf.size(font_id, 14, 72)
    for obj in getObjectWithIDKeys(self.idkey, self.show_only_selected):
        position=get2DPosition(getCenter(obj), context)
        blf.position(font_id, position[0], position[1], 0)
        blf.draw(font_id, str(obj[self.idkey]))

    blf.position(font_id, 20, 20, 0)
    blf.size(font_id, 12, 72)
    blf.draw(font_id, "%s displayed - Esc to Quit" % self.idKeyName)

class IDKeysIntegerDraw(bpy.types.Operator):
    bl_idname = "an.id_keys_integer_draw"
    bl_label = "Show ID Keys"
    bl_description = "Show ID Keys in 3D viewport"
    bl_options = {"INTERNAL"}
    
    idKeyName: bpy.props.StringProperty()
    idkey: bpy.props.StringProperty()
    show_only_selected: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return not context.window_manager.an_3d_draw_isrunning
        
    def __init__(self):
        bpy.context.window_manager.an_3d_draw_isrunning=True
        self.idkey=getIDKeyIntegerName(self.idKeyName)
    
    def modal(self, context, event):
        for area in get3DAreas(): 
            area.tag_redraw()
        if event.type in {'ESC'}:
            self.finish(context)
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            # the arguments we pass the the callback
            args = (self, context)
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

    def finish(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        bpy.context.window_manager.an_3d_draw_isrunning=False

def register():
    bpy.types.WindowManager.an_3d_draw_isrunning = BoolProperty()

def unregister():
    del bpy.types.WindowManager.an_3d_draw_isrunning
