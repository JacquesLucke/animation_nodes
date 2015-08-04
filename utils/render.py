import bpy
from bpy.app.handlers import persistent

def isRendering():
    return _isRendering

_isRendering = False

@persistent
def renderIsStarting(scene):
    global _isRendering
    _isRendering = True

@persistent
def renderIsEnding(scene):
    global _isRendering
    _isRendering = False


def register_handlers():
    bpy.app.handlers.render_pre.append(renderIsStarting)
    bpy.app.handlers.render_post.append(renderIsEnding)

def unregister_handlers():
    bpy.app.handlers.render_pre.remove(renderIsStarting)
    bpy.app.handlers.render_post.remove(renderIsEnding)
