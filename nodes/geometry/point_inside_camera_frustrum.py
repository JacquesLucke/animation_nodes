import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
import bpy_extras

class PointInCameraFrustrum(bpy.types.Node, AnimationNode):
    bl_idname = "an_PointInCameraFrustrum"
    bl_label = "Point in Camera Frustrum"
    
    def create(self):
        self.newInput("Scene", "Scene", "scene", hide = True)
        self.newInput("Object", "Camera", "camera")
        self.newInput("Vector", "3d Point", "point", value=(0, 0, 0))
        self.newInput("Float", "Threshold % (positive = interior)", "threshold", value = 0.0)
        
        self.newOutput("Float", "Image u", "u")
        self.newOutput("Float", "Image v", "v")
        self.newOutput("Float", "Z depth", "z")
        self.newOutput("Boolean", "Is in frustrum", "visible")
        
    def getExecutionCode(self):
        yield "u, v, z, visible = self.isInFrustrum(scene, camera, point, threshold)"
            
    def getUsedModules(self):
        return ["bpy_extras"]
    
    def isInFrustrum(self, scene, camera, point, threshold):
        if camera is None:
            return 0, 0, 0, False, 0
        if camera.type != 'CAMERA':
            return 0, 0, 0, False, 0
        co = bpy_extras.object_utils.world_to_camera_view(scene, camera, point)
        cs, ce = camera.data.clip_start, camera.data.clip_end
        th = threshold / 100
        if th > 0.5:
            th = 0.5
        limit = 0.5 - th
        u = co.x
        v = co.y
        z = co.z
        visible = (0.0 + th < u < 1.0 - th and 0.0 + th < v < 1.0 - th and cs < z <  ce)
        return u, v, z, visible
