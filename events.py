import bpy
from bpy.app.handlers import persistent
from . utils.recursion import noRecursion

class EventState:
    def __init__(self):
        self.reset()

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
        if self.sceneChanged: events.add("Scene")
        if self.frameChanged: events.add("Frame")
        if self.addonChanged: events.add("Addon")
        if self.propertyChanged: events.add("Property")
        return events

event = EventState()
treeUpdatedWhileWorking = False

@persistent
def sceneUpdated(scene):
    event.sceneChanged = True
    update(event.getActives())
    event.reset()

@persistent
def frameChanged(scene):
    event.frameChanged = True

@persistent
def fileLoaded(scene):
    event.fileChanged = True

def addonChanged():
    event.addonChanged = True

def propertyChanged(self = None, context = None):
    event.propertyChanged = True

def executionCodeChanged(self = None, context = None):
    treeChanged()

def treeChanged(self = None, context = None):
    global treeUpdatedWhileWorking
    treeUpdatedWhileWorking = True
    event.treeChanged = True


from . node_link_conversion import correctForbiddenNodeLinks
from . import tree_info
from . utils.nodes import iterAnimationNodes

@noRecursion
def update(events):
    print(events)
    if "Tree" in events:
        updateNodes()
        tree_info.update()
        correctForbiddenNodeLinks()

def updateNodes():
    updateAllNodes()

def updateAllNodes():
    for node in iterAnimationNodes():
        updateDataIfNecessary()
        node.edit()

def updateDataIfNecessary():
    global treeUpdatedWhileWorking
    if treeUpdatedWhileWorking:
        tree_info.update()
        treeUpdatedWhileWorking = False



# Register
##################################

def registerHandlers():
    bpy.app.handlers.scene_update_post.append(sceneUpdated)
    bpy.app.handlers.frame_change_post.append(frameChanged)
    bpy.app.handlers.load_post.append(fileLoaded)
    addonChanged()

def unregisterHandlers():
    bpy.app.handlers.frame_change_post.remove(frameChanged)
    bpy.app.handlers.scene_update_post.remove(sceneUpdated)
    bpy.app.handlers.load_post.remove(fileLoaded)
