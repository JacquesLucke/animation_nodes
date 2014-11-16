import bpy, time
from bpy.app.handlers import persistent
from mn_utils import *
from mn_cache import clearExecutionCache
from mn_execution_unit_generator import getExecutionUnits
from bpy.props import *
from mn_selection_utils import *
from mn_node_utils import *

COMPILE_BLOCKER = 0
executionUnits = []

def updateAnimationTrees(event = "NONE"):
	if COMPILE_BLOCKER <= 0:
		forbidCompiling()
		
		start = time.clock()
		updateSettingNodes = getAndResetUpdateSettingsNodes()
		
		for executionUnit in executionUnits:
			executionUnit.execute(event)
			
		resetForceUpdateProperties(updateSettingNodes)
		clearExecutionCache()
		timeSpan = time.clock() - start
		
		if bpy.context.scene.mn_settings.developer.printUpdateTime:
			printTimeSpan("Update Time ", timeSpan)
			
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
	
def getAndResetUpdateSettingsNodes():
	nodes = getNodesFromType("mn_NetworkUpdateSettingsNode")
	for node in nodes:
		node.executionTime = 0.0
	return nodes
def resetForceUpdateProperties(nodes):
	for node in nodes:
		node.settings.forceExecution = False
			
		
		
# generate Scripts
################################

def generateExecutionUnits():
	global executionUnits
	
	if COMPILE_BLOCKER <= 0:
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
	updateAnimationTrees("FRAME")
@persistent
def sceneUpdateHandler(scene):
	updateSelectionSorting()
	updateAnimationTrees("SCENE")
@persistent
def fileLoadHandler(scene):
	generateExecutionUnits()
	updateAnimationTrees()
def nodePropertyChanged(self, context):
	updateAnimationTrees("PROPERTY")
def settingPropertyChanged(self, context):
	generateExecutionUnits()
	updateAnimationTrees("PROPERTY")
def nodeTreeChanged(self = None, context = None):
	generateExecutionUnits()
	updateAnimationTrees("TREE")
	
	
bpy.app.handlers.frame_change_post.append(frameChangeHandler)
bpy.app.handlers.scene_update_post.append(sceneUpdateHandler)
bpy.app.handlers.load_post.append(fileLoadHandler)