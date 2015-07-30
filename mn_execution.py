import bpy, time, traceback, sys
from bpy.app.handlers import persistent
from bpy.props import *
from . mn_utils import *
from . mn_cache import clearExecutionCache
from . utils.mn_node_utils import *
from . utils.selection import updateSelectionSorting
from . mn_execution_unit_generator import getExecutionUnits
from . manage_broken_files import containsBrokenNodes

COMPILE_BLOCKER = 0
executionUnits = []

def updateAnimationTrees(event = "NONE", sender = None):
    if COMPILE_BLOCKER == 0 and len(executionUnits) > 0:
        forbidCompiling()
        
        start = time.clock()
        
        secureExecution(event, sender)
        clearExecutionCache()
        
        timeSpan = time.clock() - start
        
        if bpy.context.scene.mn_settings.developer.printUpdateTime:
            printTimeSpan("Update Time ", timeSpan)
                  
        try:
            bpy.context.scene.update()
            if bpy.context.scene.mn_settings.update.redrawViewport:
                redraw_areas_if_possible()
        except: pass
            
        allowCompiling()
        
def secureExecution(event, sender):
    try: executeUnits(event, sender)
    except:
        resetCompileBlocker()
        generateExecutionUnits()
        forbidCompiling()
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
    global COMPILE_BLOCKER
    COMPILE_BLOCKER = max(COMPILE_BLOCKER - 1, 0)
def forbidCompiling():
    global COMPILE_BLOCKER
    COMPILE_BLOCKER += 1
def resetCompileBlocker():
    global COMPILE_BLOCKER
    COMPILE_BLOCKER = 0
            
        
# generate Scripts
################################

def generateExecutionUnits():
    global executionUnits
    
    if containsBrokenNodes():
        executionUnits = []
        return
    
    if COMPILE_BLOCKER == 0:
        forbidCompiling()
        
        start = time.clock()
        executionUnits = getExecutionUnits()
        timeSpan = time.clock() - start
        if bpy.context.scene.mn_settings.developer.printGenerationTime:
            print("Script Gen. " + str(round(timeSpan, 7)) + " s  -  " + str(round(1/timeSpan, 5)) + " fps")
        
        allowCompiling()
        
def getCodeStrings():
    codeStrings = []
    for executionUnit in executionUnits:
        codeStrings.append(executionUnit.executionCode)
    return codeStrings
    
    
# handlers to start the update
##############################

@persistent
def frameChangeHandler(scene):
    if is_rendering and scene.mn_settings.update.resetCompileBlockerWhileRendering:
        resetCompileBlocker()
    updateAnimationTrees("FRAME")
@persistent
def sceneUpdateHandler(scene):
    updateSelectionSorting()
    updateAnimationTrees("SCENE")
@persistent
def fileLoadHandler(scene):
    generateExecutionUnits()
def nodePropertyChanged(self = None, context = None):
    updateAnimationTrees("PROPERTY")
def settingPropertyChanged(self, context):
    generateExecutionUnits()
    updateAnimationTrees("PROPERTY")
def nodeTreeChanged(self = None, context = None):
    generateExecutionUnits()
    updateAnimationTrees("TREE")
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