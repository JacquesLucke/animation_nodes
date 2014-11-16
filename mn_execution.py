import bpy, time
from bpy.app.handlers import persistent
from mn_utils import *
from mn_cache import clearExecutionCache
from mn_network_code_generator import getExecutionUnits
from bpy.props import *
from mn_selection_utils import *
from mn_node_utils import *

COMPILE_BLOCKER = 0

compiledCodeObjects = []
codeStrings = []

executionUnits = []

def updateAnimationTrees(treeChanged, event = "NONE"):
	if COMPILE_BLOCKER <= 0:
		forbidCompiling()
		start = time.clock()
		scene = bpy.context.scene
		if treeChanged:
			rebuildNodeNetworks()
		for executionUnit in executionUnits:
			executionUnit.execute(event)
		resetForceUpdateProperties()
		clearExecutionCache()
		if scene.mn_settings.developer.printUpdateTime:
			timeSpan = time.clock() - start
			print("Exec. " + str(round(timeSpan, 7)) + " s  -  " + str(round(1/timeSpan, 5)) + " fps")
		allowCompiling()
			
def allowCompiling():
	global COMPILE_BLOCKER
	COMPILE_BLOCKER = max(COMPILE_BLOCKER - 1, 0)
def forbidCompiling():
	global COMPILE_BLOCKER
	COMPILE_BLOCKER += 1
def resetCompileBlocker():
	global COMPILE_BLOCKER
	COMPILE_BLOCKER = 0
	
def resetForceUpdateProperties():
	nodes = getNodesFromType("mn_NetworkUpdateSettingsNode")
	for node in nodes:
		node.settings.forceExecution = False
			
			
# compile code objects
################################

def rebuildNodeNetworks():
	global compiledCodeObjects, executionUnits
	del compiledCodeObjects[:]
	del codeStrings[:]
	start = time.clock()
	scene = bpy.context.scene
	executionUnits = getExecutionUnits()
	timeSpan = time.clock() - start
	if scene.mn_settings.developer.printGenerationTime:  print("Script Gen. " + str(round(timeSpan, 7)) + " s  -  " + str(round(1/timeSpan, 5)) + " fps")
		
def getCodeStrings():
	codeStrings = []
	for executionUnit in executionUnits:
		codeStrings.append(executionUnit.executionCode)
	return codeStrings
	
	
	
# handlers to start the update
##############################

	
@persistent
def frameChangeHandler(scene):
	updateAnimationTrees(False, "FRAME")
@persistent
def sceneUpdateHandler(scene):
	updateSelectionSorting()
	updateAnimationTrees(False, "SCENE")
@persistent
def fileLoadHandler(scene):
	updateAnimationTrees(True)
def nodePropertyChanged(self, context):
	updateAnimationTrees(False, "PROPERTY")
def settingPropertyChanged(self, context):
	updateAnimationTrees(True, "PROPERTY")
def nodeTreeChanged(self = None, context = None):
	updateAnimationTrees(True, "TREE")
	
	
bpy.app.handlers.frame_change_post.append(frameChangeHandler)
bpy.app.handlers.scene_update_post.append(sceneUpdateHandler)
bpy.app.handlers.load_post.append(fileLoadHandler)