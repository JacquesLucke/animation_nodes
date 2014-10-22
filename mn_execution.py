import bpy, time
from bpy.app.handlers import persistent
from mn_utils import *
from mn_cache import clearExecutionCache
from mn_network_code_generator import getAllNetworkCodeStrings

ALLOW_COMPILING = True

compiledCodeObjects = []
codeStrings = []

def updateAnimationTrees(treeChanged = True):
	if ALLOW_COMPILING:
		forbidCompiling()
		start = time.clock()
		if treeChanged:
			rebuildNodeNetworks()
		for i, codeObject in enumerate(compiledCodeObjects):
			if bpy.context.scene.showFullError: 
				exec(codeObject, {})
			else:
				try: exec(codeObject, {})
				except BaseException as e:
					rebuildNodeNetworks()
					try: exec(codeObject, {})
					except BaseException as e: print(e)
		clearExecutionCache()
		if bpy.context.scene.printUpdateTime:
			timeSpan = time.clock() - start
			print("Exec. " + str(round(timeSpan, 7)) + " s  -  " + str(round(1/timeSpan, 5)) + " fps")
		allowCompiling()
			
def allowCompiling():
	global ALLOW_COMPILING
	ALLOW_COMPILING = True
def forbidCompiling():
	global ALLOW_COMPILING
	ALLOW_COMPILING = False
			
			
# compile code objects
################################

def rebuildNodeNetworks():
	global compiledCodeObjects, codeStrings
	del compiledCodeObjects[:]
	del codeStrings[:]
	start = time.clock()
	if bpy.context.scene.showFullError: codeStrings = getAllNetworkCodeStrings()
	else:
		try: codeStrings = getAllNetworkCodeStrings()
		except BaseException as e: pass
	for code in codeStrings:
		compiledCodeObjects.append(compile(code, "<string>", "exec"))
	timeSpan = time.clock() - start
	if bpy.context.scene.printScriptGenerationTime:  print("Script Gen. " + str(round(timeSpan, 7)) + " s  -  " + str(round(1/timeSpan, 5)) + " fps")
		
def getCodeStrings():
	return codeStrings
	
	
	
# handlers to start the update
##############################

	
@persistent
def frameChangeHandler(scene):
	if scene.updateAnimationTreeOnFrameChange:
		updateAnimationTrees(False)
@persistent
def sceneUpdateHandler(scene):
	if scene.updateAnimationTreeOnSceneUpdate and not bpy.context.screen.is_animation_playing:
		updateAnimationTrees(False)
@persistent
def fileLoadHandler(scene):
	updateAnimationTrees(True)
def nodePropertyChanged(self, context):
	if context.scene.updateAnimationTreeOnPropertyChange:
		updateAnimationTrees(False)
def settingPropertyChanged(self, context):
	updateAnimationTrees(True)
def nodeTreeChanged(self = None, context = None):
	updateAnimationTrees(True)
	
bpy.types.Scene.updateAnimationTreeOnFrameChange = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Frame Change")
bpy.types.Scene.updateAnimationTreeOnSceneUpdate = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Scene Update")
bpy.types.Scene.updateAnimationTreeOnPropertyChange = bpy.props.BoolProperty(default = True, name = "Update Animation Tree On Property Change")

bpy.types.Scene.printUpdateTime = bpy.props.BoolProperty(default = False, name = "Print Update Time")
bpy.types.Scene.printScriptGenerationTime = bpy.props.BoolProperty(default = False, name = "Print Script Generation Time")
bpy.types.Scene.showFullError = bpy.props.BoolProperty(default = False, name = "Show Full Error")
bpy.types.Scene.nodeExecutionProfiling = bpy.props.BoolProperty(default = False, name = "Node Execution Profiling", update = settingPropertyChanged)

	
bpy.app.handlers.frame_change_post.append(frameChangeHandler)
bpy.app.handlers.scene_update_post.append(sceneUpdateHandler)
bpy.app.handlers.load_post.append(fileLoadHandler)