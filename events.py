import bpy
from . import tree_info
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
        return events

event = EventState()


@persistent
def sceneUpdated(scene):
    event.sceneChanged = True
    evaluateRaisedEvents()

@persistent
def renderFramePre(scene):
    event.frameChanged = True
    evaluateRaisedEvents()

def evaluateRaisedEvents():
    event_handler.update(event.getActives())
    event.reset()


@persistent
def frameChanged(scene):
    event.frameChanged = True

def propertyChanged(self = None, context = None):
    event.propertyChanged = True

@persistent
def fileLoaded(scene):
    event.fileChanged = True
    treeChanged()

def addonChanged():
    event.addonChanged = True
    treeChanged()

def executionCodeChanged(self = None, context = None):
    treeChanged()

def networkChanged(self = None, context = None):
    treeChanged()

def treeChanged(self = None, context = None):
    event.treeChanged = True
    tree_info.treeChanged()


@persistent
def renderInitialized(scene):
    event.isRendering = True

@persistent
def renderCanceled(scene):
    event.isRendering = False

@persistent
def renderCompleted(scene):
    event.isRendering = False

def isRendering():
    return event.isRendering



# Register
##################################

def registerHandlers():
    bpy.app.handlers.scene_update_post.append(sceneUpdated)
    bpy.app.handlers.frame_change_post.append(frameChanged)
    bpy.app.handlers.load_post.append(fileLoaded)

    bpy.app.handlers.render_init.append(renderInitialized)
    bpy.app.handlers.render_pre.append(renderFramePre)
    bpy.app.handlers.render_cancel.append(renderCanceled)
    bpy.app.handlers.render_complete.append(renderCompleted)

    addonChanged()

def unregisterHandlers():
    bpy.app.handlers.frame_change_post.remove(frameChanged)
    bpy.app.handlers.scene_update_post.remove(sceneUpdated)
    bpy.app.handlers.load_post.remove(fileLoaded)

    bpy.app.handlers.render_init.remove(renderInitialized)
    bpy.app.handlers.render_pre.remove(renderFramePre)
    bpy.app.handlers.render_cancel.remove(renderCanceled)
    bpy.app.handlers.render_complete.remove(renderCompleted)
