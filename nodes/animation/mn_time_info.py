import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *

class mn_TimeInfoNode(Node, AnimationNode):
	bl_idname = "mn_TimeInfoNode"
	bl_label = "Time Info"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_FloatSocket", "Frame")
		self.outputs.new("mn_FloatSocket", "Start Frame")
		self.outputs.new("mn_FloatSocket", "End Frame")
		self.outputs.new("mn_FloatSocket", "Frame Rate")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Frame" : "frame",
				"Start Frame" : "start_frame",
				"End Frame" : "end_frame",
				"Frame Rate" : "frame_rate"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		codeLines.append("scene = bpy.context.scene")
		if outputUse["Frame"]: codeLines.append("$frame$ = scene.frame_current_final")
		if outputUse["Start Frame"]: codeLines.append("$start_frame$ = scene.frame_start")
		if outputUse["End Frame"]: codeLines.append("$end_frame$ = scene.frame_end")
		if outputUse["Frame Rate"]: codeLines.append("$frame_rate$ = scene.render.fps")
		return "\n".join(codeLines)