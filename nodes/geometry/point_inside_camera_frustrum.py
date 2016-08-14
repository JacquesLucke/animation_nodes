import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
import bpy_extras

class PointInsideCameraFrustrum(bpy.types.Node, AnimationNode):
    bl_idname = "an_PointInsideCameraFrustrum"
    bl_label = "Point inside Camera Frustrum"
    
    def create(self):
        self.newInput("Scene", "scene", "scene", hide = True)
        self.newInput("Object", "Camera", "camera")
        self.newInput("Vector", "3d Point", "point", value=(0, 0, 0))
        self.newInput("Float", "Threshold % (positive = interior)", "threshold", value = 0.0)
        self.newInput("Float", "Fade Area %", "fadearea", value = 10.0)
        
        self.newOutput("Float", "Image u", "u")
        self.newOutput("Float", "Image v", "v")
        self.newOutput("Float", "Fade", "fade")
        self.newOutput("Boolean", "Is in frustrum", "visible")
        
    def getExecutionCode(self):
        yield "u, v, visible, fade = self.isInFrustrum(scene, camera, point, threshold, fadearea)"
            
    def getUsedModules(self):
        return ["bpy_extras"]
    
    def isInFrustrum(self, scene, camera, point, threshold, fadearea):
        if camera is None:
            return 0, 0, False, 0
        if camera.type != 'CAMERA':
            return 0, 0, False, 0
        co = bpy_extras.object_utils.world_to_camera_view(scene, camera, point)
        cs, ce = camera.data.clip_start, camera.data.clip_end
        th, fa = threshold / 100, fadearea / 100
        limit = 0.5 - th
        if th > 0.5:
            th = 0.5
        u = co.x
        v = co.y
        visible = (0.0 + th < co.x < 1.0 - th and 0.0 + th < co.y < 1.0 - th and cs < co.z <  ce)
        fu = (limit - abs(u - 0.5)) / fa
        fv = (limit - abs(v - 0.5)) / fa 
        if fu > fv:
            fade = fv
        else:
            fade = fu
        if fade > 1:
            fade = 1
        return u, v, visible, fade
