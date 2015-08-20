import bpy
from . import event_handler
from bpy.app.handlers import persistent

class EventState:
    def __init__(self):
        self.reset()
        self.isRendering = False

    def reset(self):
        self.treeChanged = False
        self.fileChanged = False
        self.sceneChanged = False
        self.frameChanged = False
        self.addonChanged = False
        self.propertyChanged = False

    def getActives(self):
        events = set()
        if self.treeChanged: events.add("Tree")
        if self.fileChanged: events.add("File")
        if self.addonChanged: events.add("Addon")
        if self.sceneChanged: events.add("Scene")
        if self.frameChanged: events.add("Frame")
        if self.propertyChanged: events.add("Property")
        if self.isRendering: events.add("Render")
        return events

event = EventState()
treeUpdatedWhileWorking = False

@persistent
def sceneUpdated(scene):
    event.sceneChanged = True
    event_handler.update(event.getActives())
    event.reset()

@persistent
def frameChanged(scene):
    event.frameChanged = True

@persistent
def fileLoaded(scene):
    event.fileChanged = True
    event_handler.treeNeedsUpdate()

def addonChanged():
    event.addonChanged = True
    event_handler.treeNeedsUpdate()

def propertyChanged(self = None, context = None):
    event.propertyChanged = True

def executionCodeChanged(self = None, context = None):
    treeChanged()

def networkChanged(self = None, context = None):
    treeChanged()

def treeChanged(self = None, context = None):
    event.treeChanged = True
    event_handler.treeNeedsUpdate()

@persistent
def renderIsStarting(scene):
    event.isRendering = True

@persistent
def renderIsEnding(scene):
    event.isRendering = False



# Register
##################################

def registerHandlers():
    bpy.app.handlers.scene_update_post.append(sceneUpdated)
    bpy.app.handlers.frame_change_post.append(frameChanged)
    bpy.app.handlers.load_post.append(fileLoaded)

    bpy.app.handlers.render_pre.append(renderIsStarting)
    bpy.app.handlers.render_init.append(renderIsStarting)
    bpy.app.handlers.render_post.append(renderIsEnding)
    bpy.app.handlers.render_cancel.append(renderIsEnding)
    bpy.app.handlers.render_complete.append(renderIsEnding)

    addonChanged()

def unregisterHandlers():
    bpy.app.handlers.frame_change_post.remove(frameChanged)
    bpy.app.handlers.scene_update_post.remove(sceneUpdated)
    bpy.app.handlers.load_post.remove(fileLoaded)

    bpy.app.handlers.render_pre.remove(renderIsStarting)
    bpy.app.handlers.render_init.remove(renderIsStarting)
    bpy.app.handlers.render_post.remove(renderIsEnding)
    bpy.app.handlers.render_cancel.remove(renderIsEnding)
    bpy.app.handlers.render_complete.remove(renderIsEnding)
