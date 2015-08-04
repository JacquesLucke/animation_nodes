import bpy, time, traceback, sys
from bpy.app.handlers import persistent
from bpy.props import *
from . old_utils import *
from . cache import clearExecutionCache
from . utils.nodes import *
from . execution_unit_generator import getExecutionUnits

executionUnits = []
isExecuting = False
def updateAnimationTrees(event = "NONE", sender = None):
    global isExecuting
    if not isExecuting:
        isExecuting = True

        if len(executionUnits) > 0:
            start = time.clock()

            secureExecution(event, sender)
            clearExecutionCache()


            try:
                bpy.context.scene.update()
                if bpy.context.scene.an_settings.update.redrawViewport:
                    redraw_areas_if_possible()
            except: pass

        isExecuting = False

def secureExecution(event, sender):
    try: executeUnits(event, sender)
    except:
        resetCompileBlocker()
        generateExecutionUnits()
        try: executeUnits(event, sender)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            print(e)


def executeUnits(event, sender):
    for executionUnit in executionUnits:
        executionUnit.execute(event, sender)

def redraw_areas_if_possible():
    try:
        for area in bpy.context.screen.areas:
            area.tag_redraw()
    except: pass

def allowCompiling():
    pass
def forbidCompiling():
    pass
def resetCompileBlocker():
    pass


# generate Scripts
################################

def generateExecutionUnits():
    global executionUnits

    start = time.clock()
    executionUnits = getExecutionUnits()
    timeSpan = time.clock() - start
    if bpy.context.scene.an_settings.developer.printGenerationTime:
        print("Script Gen. " + str(round(timeSpan, 7)) + " s  -  " + str(round(1/timeSpan, 5)) + " fps")


def getCodeStrings():
    codeStrings = []
    for executionUnit in executionUnits:
        codeStrings.append(executionUnit.executionCode)
    return codeStrings


# handlers to start the update
##############################

propertyChanged = False
frameChanged = False
treeChanged = False

@persistent
def frameChangeHandler(scene):
    global frameChanged
    frameChanged = True

@persistent
def sceneUpdateHandler(scene):
    global treeChanged, propertyChanged, frameChanged

    if treeChanged:
        generateExecutionUnits()
        updateAnimationTrees("TREE")
        treeChanged = False

    if propertyChanged:
        updateAnimationTrees("PROPERTY")
        propertyChanged = False

    if frameChanged:
        updateAnimationTrees("FRAME")
        frameChanged = False

    updateAnimationTrees("SCENE")

@persistent
def fileLoadHandler(scene):
    generateExecutionUnits()

def nodePropertyChanged(self = None, context = None):
    global propertyChanged
    propertyChanged = True

def nodeTreeChanged(self = None, context = None):
    global treeChanged
    treeChanged = True

def forceExecution(sender = None):
    generateExecutionUnits()
    updateAnimationTrees("FORCE", sender)


# check rendering status
##############################

is_rendering = False
@persistent
def rendering_starts(scene):
    global is_rendering
    is_rendering = True
@persistent
def rendering_ends(scene):
    global is_rendering
    is_rendering = False


def register_handlers():
    bpy.app.handlers.frame_change_post.append(frameChangeHandler)
    bpy.app.handlers.scene_update_post.append(sceneUpdateHandler)
    bpy.app.handlers.load_post.append(fileLoadHandler)
    bpy.app.handlers.render_pre.append(rendering_starts)
    bpy.app.handlers.render_post.append(rendering_ends)

def unregister_handlers():
    bpy.app.handlers.frame_change_post.remove(frameChangeHandler)
    bpy.app.handlers.scene_update_post.remove(sceneUpdateHandler)
    bpy.app.handlers.load_post.remove(fileLoadHandler)
    bpy.app.handlers.render_pre.remove(rendering_starts)
    bpy.app.handlers.render_post.remove(rendering_ends)
