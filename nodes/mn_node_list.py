def getNodeNameDictionary():
	nodes = []
	
	nodes.append(("Number", [
		("mn_FloatInputNode", "Float"),
		("mn_IntegerInputNode", "Integer"),
		("mn_FloatListInputNode", "Float List"),
		("mn_RandomNumberNode", "Random"),
		("mn_FloatWiggle", "Wiggle"),
		("mn_AnimateFloatNode", "Animate"),
		("mn_FloatMathNode", "Math"),
		("mn_FloatClamp", "Clamp") ] ))
		
	nodes.append(("Vector", [
		("mn_CombineVector", "Combine Vector"),
		("mn_SeparateVector", "Separate Vector"),
		("mn_RandomVectorNode", "Random Vector"),
		("mn_VectorWiggle", "Vector Wiggle"),
		("mn_VectorLengthNode", "Vector Length"),
		("mn_AnimateVectorNode", "Animate Vector"),
		("mn_VectorDistanceNode", "Vector Distance"),
		("mn_DirectionToRotation", "Direction to Rotation"),
		("mn_TransfromVector", "Transform Vector"),
		("mn_VectorMathNode", "Vector Math") ] ))	
		
	nodes.append(("Text", [
		("mn_StringInputNode", "Text"),
		("mn_StringListInputNode", "Text List"),
		("mn_RandomStringNode", "Random Text"),
		("mn_TextBlockReader", "Text Block Reader"),
		("mn_CharactersNode", "Characters"),
		("mn_CombineStringsNode", "Combine Texts"),
		("mn_SplitText", "Split Text"),
		("mn_ReplicateStringsNode", "Replicate Text"),
		("mn_SubstringNode", "Trim Text"),
		("mn_StringAnalyzeNode", "Analyze Text"),
		("mn_TextOutputNode", "Text Output") ] ))
	
	nodes.append(("Object", [
		("mn_ObjectInputNode", "Object"),
		("mn_ObjectListInputNode", "Object List"),
		("mn_ObjectInfoNode", "Object Info"),
		("mn_ObjectMatrixInput", "Object Matrices"),
		("mn_ObjectKeyframeInput", "Keyframe"),
		("mn_ReplicateObjectNode", "Replicate Object"),
		("mn_CopyObjectData", "Copy Data"),
		("mn_ObjectAttributeInputNode", "Attribute Input"),
		("mn_ObjectAttributeOutputNode", "Attribute Output"),
		("mn_CopyTransformsNode", "Copy Transforms"),
		("mn_ObjectMatrixOutputNode", "Object Matrix Output"),
		("mn_ObjectOutputNode", "Transforms Output") ] ))
		
	nodes.append(("Matrix", [
		("mn_ComposeMatrix", "Compose Matrix"),
		("mn_DecomposeMatrix", "Decompose Matrix"),
		("mn_TranslationMatrix", "Translation Matrix"),
		("mn_RotationMatrix", "Rotation Matrix"),
		("mn_ScaleMatrix", "Scale Matrix"),
		("mn_MatrixCombine", "Combine Matrices"),
		("mn_MatrixMath", "Matrix Math"),
		("mn_AnimateMatrixNode", "Animate Matrix"),
		("mn_InvertMatrix", "Invert Matrix") ] ))
		
	nodes.append(("Mesh", [
		("mn_MeshInfo", "Mesh Info"),
		("mn_VertexInfo", "Vertex Info"),
		("mn_PolygonInfo", "Polygon Info") ] ))
		
	nodes.append(("List", [
		("mn_GetListElementNode", "Get Element"),
		("mn_SetListElementNode", "Set Element"),
		("mn_GetListLengthNode", "Get Length"),
		("mn_CombineListsNode", "Combine Lists"),
		("mn_ShuffleListNode", "Shuffle"),
		("mn_SumListElementsNode", "Sum Elements") ] ))
		
	nodes.append(("Sound", [
		("mn_SoundBakeNode", "Sound Bake"),
		("mn_SoundInputNode", "Sound Input") ] ))
		
	nodes.append(("Color", [
		("mn_ColorInputNode", "RGB"),
		("mn_CombineColor", "Combine RGBA"),
		("mn_ColorMix", "Mix"),
		("mn_SetVertexColor", "Set Vertex Color") ] ))
		
	nodes.append(("Animation", [
		("mn_TimeInfoNode", "Time Info"),
		("mn_InterpolationNode", "Interpolation"),
		("mn_EvaluateInterpolation", "Evaluate Interpolation"),
		("mn_MixInterpolation", "Mix Interpolation") ] ))
		
	nodes.append(("Debug", [
		("mn_DebugOutputNode", "Socket Values"),
		("mn_DebugVectorOutputNode", "Vector Socket Value") ] ))
			
	nodes.append(("Material", [
		("mn_CyclesMaterialOutputNode", "Cycles Material Output"),
		("mn_ViewportColorNode" , "Viewport Color") ] ))

	nodes.append(("Convert", [
		("mn_ConvertNode", "Convert") ] ))
		
	nodes.append(("Script", [
		("mn_ExpressionNode", "Expression"),
		("mn_ScriptNode", "Script") ] ))
		
	nodes.append(("System", [
		("mn_LoopCallerNode", "Loop Caller"),
		("mn_LoopStartNode", "Generic Loop", {"preset" : repr("NONE")}),
		("mn_LoopStartNode", "Object Loop", {"preset" : repr("OBJECT")}) ] ))
		
	return nodes
