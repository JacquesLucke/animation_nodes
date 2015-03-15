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
		("mn_TextBlockWriter", "Text Block Writer"),
		("mn_SeparateTextObject", "Separate Text Object"),
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
		("mn_ObjectGroupInput", "Object Group Input"),
		("mn_ObjectInfoNode", "Object Info"),
		("mn_ObjectMatrixInput", "Object Matrices"),
		("mn_ObjectKeyframeInput", "Keyframe"),
		("mn_ObjectInstancer", "Object Instancer"),
		("mn_CopyObjectData", "Copy Data"),
		("mn_ObjectAttributeInputNode", "Attribute Input"),
		("mn_ObjectAttributeOutputNode", "Attribute Output"),
		("mn_CopyTransformsNode", "Copy Transforms"),
		("mn_ObjectMatrixOutputNode", "Object Matrix Output"),
		("mn_ObjectTransformsOutput", "Transforms Output") ] ))
		
	nodes.append(("Boolean", [
		("mn_BooleanInputNode", "Boolean"),
		("mn_CompareNode", "Compare"),
		("mn_InvertNode", "Invert"),
		("mn_ConditionNode", "Condition")] ))
		
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
		("mn_ObjectMeshInfo", "Object Mesh Info"),
		("mn_VertexInfo", "Vertex Info"),
		("mn_TransformVertex", "Transform Vertex"),
		("mn_PolygonInfo", "Polygon Info"),
		("mn_TransformPolygon", "Transform Polygon"),
		("mn_CombineMeshData", "Recombine Mesh Data"),
		("mn_AppendToMeshData", "Append Mesh Data"),
		("mn_SeparateMeshData", "Separate Mesh Data"),
		("mn_MeshRecalculateFaceNormals", "Recalculate Normals"),
		("mn_MeshRemoveDoubles", "Remove Doubles"),
		("mn_CreateMeshFromData", "Create Mesh from Data"),
		("mn_SetMeshOnObject", "Set Mesh on Object") ] ))
		
	nodes.append(("List", [
		("mn_GetListElementNode", "Get Element"),
		("mn_SetListElementNode", "Set Element"),
		("mn_GetListLengthNode", "Get Length"),
		("mn_CombineListsNode", "Combine Lists"),
		("mn_ShuffleListNode", "Shuffle"),
		("mn_SumListElementsNode", "Sum Elements"),
		("mn_AppendListNode", "Append to List"),
		("mn_ReverseListNode", "Reverse List") ] ))
		
	nodes.append(("Sound", [
		("mn_SoundBakeNode", "Sound Bake"),
		("mn_SoundBakeInput", "Sound Bake Input"),
		("mn_SoundBakeReaderNode", "Sound Reader") ] ))
		
	nodes.append(("Color", [
		("mn_ColorInputNode", "RGB"),
		("mn_CombineColor", "Combine RGBA"),
		("mn_ColorMix", "Mix"),
		("mn_SetVertexColor", "Set Vertex Color") ] ))
		
	nodes.append(("Animation", [
		("mn_TimeInfoNode", "Time Info"),
		("mn_InterpolationNode", "Interpolation"),
		("mn_EvaluateInterpolation", "Evaluate Interpolation"),
		("mn_MixInterpolation", "Mix Interpolation"),
		("mn_SetKeyframesNode", "Set Keyframes")] ))
		
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
		("mn_ScriptNode", "Script"),
		("mn_ScriptNode", "Script from Clipboard", {"makeFromClipboard" : repr(True) } )] ))
		
	nodes.append(("System", [
		("mn_LoopCallerNode", "Loop"),
		("mn_GroupCaller", "Group Caller"),
		("mn_GroupInput", "Group Input"),
		("mn_GroupOutput", "Group Output"),
		("mn_NetworkUpdateSettingsNode", "Update Settings") ] ))
		
	return nodes
