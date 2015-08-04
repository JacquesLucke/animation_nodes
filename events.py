import bpy
from bpy.app.handlers import persistent

def propertyChanged(self = None, context = None):
    pass

def treeChanged(self = None, context = None):
    pass

def executionCodeChanged(self = None, context = None):
    pass

@persistent
def sceneUpdated(scene):
    pass

@persistent
def fileLoaded(scene):
    pass

@persistent
def frameChanged(scene):
    pass





def register_handlers():
    bpy.app.handlers.frame_change_post.append(frameChangeHandler)
    bpy.app.handlers.scene_update_post.append(sceneUpdateHandler)
    bpy.app.handlers.load_post.append(fileLoadHandler)

def unregister_handlers():
    bpy.app.handlers.frame_change_post.remove(frameChangeHandler)
    bpy.app.handlers.scene_update_post.remove(sceneUpdateHandler)
    bpy.app.handlers.load_post.remove(fileLoadHandler)
