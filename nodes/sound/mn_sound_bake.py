import bpy, math, os, re
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.utils.mn_object_utils import *
from animation_nodes.utils.mn_fcurve_utils import *
from animation_nodes.nodes.mn_node_helper import *
from animation_nodes.mn_cache import *

class mn_BakedSoundPropertyGroup(bpy.types.PropertyGroup):
	low = bpy.props.FloatProperty(name = "Lowest Frequency", default = 10.0)
	high = bpy.props.FloatProperty(name = "Highest Frequency", default = 5000.0)
	path = bpy.props.StringProperty(name = "Path", default = "")
	propertyName = bpy.props.StringProperty(name = "Property Path", default = "")

class mn_SoundBakeNode(Node, AnimationNode):
	bl_idname = "mn_SoundBakeNode"
	bl_label = "Sound Bake"
	
	bakedSound = bpy.props.CollectionProperty(type = mn_BakedSoundPropertyGroup)
	soundObjectName = bpy.props.StringProperty()
	filePath = bpy.props.StringProperty()
	setSyncMode = bpy.props.BoolProperty(name = "Set Audio Sync Mode", default = True)
	
	def init(self, context):
		forbidCompiling()
		self.use_custom_color = True
		self.color = [0.3, 0.6, 0.4]
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.separator()
		layout.label("Name: " + self.name)
	
		row = layout.row(align = True)
		row.prop(self, "filePath", text = "")
		selectPath = row.operator("mn.select_sound_file_path", "Select Path")
		selectPath.nodeTreeName = self.id_data.name
		selectPath.nodeName = self.name
		
		row = layout.row(align = True)
		bake = row.operator("mn.bake_sound_to_node", "Bake")
		bake.nodeTreeName = self.id_data.name
		bake.nodeName = self.name
		loadSound = row.operator("mn.set_sound_in_sequence_editor", "Load Sound")
		loadSound.filePath = self.filePath
		
		layout.separator()
		
	def draw_buttons_ext(self, context, layout):
		layout.prop(self, "setSyncMode")
		
	def getStrengthList(self, frame):
		identifier = self.id_data.name + self.name
		nodeCache = getLongTimeCache(identifier)
		intFrame = math.floor(max(frame, 0))
		if nodeCache is None:
			nodeCache = {}
			setLongTimeCache(identifier, nodeCache)
		if self.filePath not in nodeCache:
			nodeCache[self.filePath] = []
		fileCache = nodeCache[self.filePath]
		if intFrame + 1 >= len(fileCache):
			newFrameCaches = [None] * (intFrame - len(fileCache) + 2)
			fileCache.extend(newFrameCaches)
			
		if frame == intFrame:
			frameCache = fileCache[intFrame]
			if frameCache is None:
				frameCache = self.loadStrengthListAtFrame(intFrame)
				fileCache[intFrame] = frameCache
			strengthList = frameCache
		else: # for subframes
			lowerFrame = intFrame
			upperFrame = intFrame + 1
			
			lowerCache = fileCache[lowerFrame]
			if lowerCache is None:
				lowerCache = self.loadStrengthListAtFrame(intFrame)
				fileCache[lowerFrame] = lowerCache		
			upperCache = fileCache[upperFrame]
			if upperCache is None:
				upperCache = self.loadStrengthListAtFrame(intFrame)
				fileCache[upperFrame] = upperCache
			strengthList = self.mixStrengthLists(lowerCache, upperCache, frame - lowerFrame)
		return strengthList
		
	def mixStrengthLists(self, list1, list2, influence):
		strenghts = []
		for a, b in zip(list1, list2):
			strenghts.append(a * (1 - influence) + b * influence)
		return strenghts
		
	def loadStrengthListAtFrame(self, frame):
		soundObject = self.getSoundObject()
		strenghts = []
		try:
			for item in self.bakedSound:
				strenghts.append(getSingleValueAtFrame(soundObject, '["' + item.propertyName + '"]', frame))
		except: strenghts = [0]
		return strenghts
		
	def bakeSound(self):
		if self.filePath == "":
			return
		forbidCompiling()
		scene = bpy.context.scene
		oldFrame = scene.frame_current
		scene.frame_current = 1
		soundObject = self.getSoundObject()
		self.removeSoundCurves(soundObject)
		soundCombinations = [(0, 50), (50, 150), (150, 300), (300, 500), (500, 1000), (1000, 2000), (2000, 4000), (4000, 10000), (10000, 20000)]
		wm = bpy.context.window_manager
		wm.progress_begin(0.0, len(soundCombinations) - 1.0)
		wm.progress_update(0.0)
		for index, (low, high) in enumerate(soundCombinations):
			self.bakeIndividualSound(soundObject, self.filePath, low, high)
			wm.progress_update(index + 1.0)
		wm.progress_end()
		soundObject.hide = True
		self.name = re.sub(r"\W+", "", os.path.basename(self.filePath))
		loadSound(self.filePath)
		if self.setSyncMode:
			scene.sync_mode = "AUDIO_SYNC"
		scene.frame_current = oldFrame
		allowCompiling()
		nodeTreeChanged()
		
	def getSoundObject(self):
		soundObject = bpy.data.objects.get(self.soundObjectName)
		if soundObject is None:
			soundObject = bpy.data.objects.new(getPossibleObjectName("sound object"), None)
			soundObject.hide = True
			soundObject.parent = getMainObjectContainer()
			self.soundObjectName = soundObject.name
			bpy.context.scene.objects.link(soundObject)
		return soundObject
		
	def removeSoundCurves(self, soundObject):
		for item in self.bakedSound:
			fCurve = getSingleFCurveWithDataPath(soundObject, '["' + item.propertyName + '"]')
			if fCurve is not None:
				soundObject.animation_data.action.fcurves.remove(fCurve)
		self.bakedSound.clear()
		
	def bakeIndividualSound(self, soundObject, filePath, low, high):
		propertyName = "sound " + str(low) + " - " + str(high)
		propertyPath = '["' + propertyName + '"]'
		
		bpy.context.area.type = "GRAPH_EDITOR"
		soundObject.hide = False
		deselectAllFCurves(soundObject)
		soundObject[propertyName] = 0.0
		soundObject.keyframe_insert(frame = 1, data_path = propertyPath)
		deselectAll()
		setActive(soundObject)
		bpy.ops.graph.sound_bake(
			filepath = filePath,
			low = low,
			high = high)
		soundObject.hide = True
		bpy.context.area.type = "NODE_EDITOR"
		
		item = self.bakedSound.add()
		item.low = low
		item.high = high
		item.path = filePath
		item.propertyName = propertyName
		
		self.clearCache()
		
	def copy(self, node):
		self.soundObjectName = ""
		self.bakedSound.clear()
		
	def free(self):
		bpy.context.scene.objects.unlink(self.getSoundObject())
		self.clearCache()
		
	def clearCache(self):
		identifier = self.id_data.name + self.name
		setLongTimeCache(identifier, None)
		
class BakeSoundToNode(bpy.types.Operator):
	bl_idname = "mn.bake_sound_to_node"
	bl_label = "Bake Sound to Node"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.bakeSound()
		return {'FINISHED'}	
		
class SelectSoundFilePath(bpy.types.Operator):
	bl_idname = "mn.select_sound_file_path"
	bl_label = "Select Sound File"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	filepath = bpy.props.StringProperty(subtype = "FILE_PATH")
	
	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return { 'RUNNING_MODAL' }
		
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.filePath = self.filepath
		return {'FINISHED'}	
		
class SetSoundInSequenceEditor(bpy.types.Operator):
	bl_idname = "mn.set_sound_in_sequence_editor"
	bl_label = "Load Sound in Blender"
	
	filePath = bpy.props.StringProperty()
		
	def execute(self, context):
		loadSound(self.filePath)
		return {'FINISHED'}	
		
def loadSound(filePath):
	scene = bpy.context.scene
	scene.sequence_editor_clear()
	scene.sequence_editor_create()
	scene.sequence_editor.sequences.new_sound("Sound", filePath, channel = 0, frame_start = 1)

