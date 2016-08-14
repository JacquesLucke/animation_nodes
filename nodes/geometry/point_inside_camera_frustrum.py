import bpy
from bpy.props import *
from ... base_types.node import AnimationNode
import bpy_extras

class PointInCameraFrustrumNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PointInCameraFrustrumNode"
    bl_label = "Point in Camera Frustrum"
    
    def create(self):
        self.newInput("Scene", "Scene", "scene", hide = True)
        self.newInput("Object", "Camera", "camera")
        self.newInput("Vector", "Point", "point", value=(0, 0, 0))
        self.newInput("Float", "Threshold", "threshold", value = 0.0)
        
        self.newOutput("Float", "Image u", "u")
        self.newOutput("Float", "Image v", "v")
        self.newOutput("Float", "Z depth", "z")
        self.newOutput("Boolean", "Visible", "visible")
        
    def getExecutionCode(self):
        yield "u, v, z, visible = self.isInFrustrum(scene, camera, point, threshold)"
            
    def getUsedModules(self):
        return ["bpy_extras"]
    
    def isInFrustrum(self, scene, camera, point, threshold):
        if getattr(camera, "type", "") != 'CAMERA':
            return 0, 0, 0, False
        co = bpy_extras.object_utils.world_to_camera_view(scene, camera, point)
        clipStart, clipEnd = camera.data.clip_start, camera.data.clip_end
        if threshold > 0.5:
            threshold = 0.5
        limit = 0.5 - threshold
        u, v, z = co.xyz
        visible = ( 0.0 + threshold < u < 1.0 - threshold and 
                    0.0 + threshold < v < 1.0 - threshold and 
                    clipStart < z <  clipEnd)
        return u, v, z, visible
