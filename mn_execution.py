import bpy, time
from bpy.app.handlers import persistent
from mn_utils import *
from mn_cache import clearExecutionCache
from mn_network_code_generator import getAllNetworkCodeStrings
from bpy.props import *
from mn_selection_utils import *

COMPILE_BLOCKER = 0

compiledCodeObjects = []
codeStrings = []

def updateAnimationTrees(treeChanged = True):
	if COMPILE_BLOCKER <= 0:
		forbidCompiling()
		start = time.clock()
		scene = bpy.context.scene
		if treeChanged:
			rebuildNodeNetworks()
		for i, codeObject in enumerate(compiledCodeObjects):
			if scene.mn_settings.developer.showErrors: 
				exec(codeObject, {})
			else:
				try: exec(codeObject, {})
				except BaseException as e:
					rebuildNodeNetworks()
					try: exec(codeObject, {})
					except BaseException as e: print(e)
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
			
			
# compile code objects
################################

def rebuildNodeNetworks():
	global compiledCodeObjects, codeStrings
	del compiledCodeObjects[:]
	del codeStrings[:]
	start = time.clock()
	scene = bpy.context.scene
	if scene.mn_settings.developer.showErrors: codeStrings = getAllNetworkCodeStrings()
	else:
		try: codeStrings = getAllNetworkCodeStrings()
		except BaseException as e: pass
	for code in codeStrings:
		compiledCodeObjects.append(compile(code, "<string>", "exec"))
	timeSpan = time.clock() - start
	if scene.mn_settings.developer.printGenerationTime:  print("Script Gen. " + str(round(timeSpan, 7)) + " s  -  " + str(round(1/timeSpan, 5)) + " fps")
		
def getCodeStrings():
	return codeStrings
	
	
	
# handlers to start the update
##############################

	
@persistent
def frameChangeHandler(scene):
	if scene.mn_settings.update.frameChange:
		if isAnimationPlaying():
			if getCurrentFrame() % (scene.mn_settings.update.skipFramesAmount + 1) == 0:
				updateAnimationTrees(False)
		else:
			updateAnimationTrees(False)
@persistent
def sceneUpdateHandler(scene):
	updateSelectionSorting()
	if scene.mn_settings.update.sceneUpdate and not isAnimationPlaying():
		updateAnimationTrees(False)
@persistent
def fileLoadHandler(scene):
	updateAnimationTrees(True)
def nodePropertyChanged(self, context):
	if context.scene.mn_settings.update.propertyChange:
		updateAnimationTrees(False)
def settingPropertyChanged(self, context):
	updateAnimationTrees(True)
def nodeTreeChanged(self = None, context = None):
	updateAnimationTrees(True)
	
	
bpy.app.handlers.frame_change_post.append(frameChangeHandler)
bpy.app.handlers.scene_update_post.append(sceneUpdateHandler)
bpy.app.handlers.load_post.append(fileLoadHandler)