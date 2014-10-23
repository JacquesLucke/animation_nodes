def getNodeNameDictionary():
	nodes = []
	
	nodes.append(("Number", [
		("mn_FloatInputNode", "Decimal Number"),
		("mn_IntegerInputNode", "Integer"),
		("mn_FloatListInputNode", "Decimal Number List"),
		("mn_RandomNumberNode", "Random"),
		("mn_FloatWiggle", "Wiggle"),
		("mn_FloatMathNode", "Math"),
		("mn_FloatClamp", "Clamp") ] ))
		
	nodes.append(("Vector", [
		("mn_CombineVector", "Combine"),
		("mn_SeparateVector", "Separate"),
		("mn_RandomVectorNode", "Random"),
		("mn_VectorWiggle", "Wiggle"),
		("mn_VectorLengthNode", "Length"),
		("mn_AnimateVectorNode", "Animate"),
		("mn_VectorDistanceNode", "Distance"),
		("mn_VectorMathNode", "Math") ] ))	
		
	nodes.append(("Text", [
		("mn_StringInputNode", "Text"),
		("mn_StringListInputNode", "Text List"),
		("mn_RandomStringNode", "Random"),
		("mn_CharactersNode", "Characters"),
		("mn_CombineStringsNode", "Combine"),
		("mn_ReplicateStringsNode", "Replicate"),
		("mn_SubstringNode", "Slice"),
		("mn_StringAnalyzeNode", "Analyze"),
		("mn_TextOutputNode", "Text Object Output") ] ))
	
	nodes.append(("Object", [
		("mn_ObjectInputNode", "Object"),
		("mn_ObjectListInputNode", "Object List"),
		("mn_ObjectInfoNode", "Info"),
		("mn_ReplicateObjectNode", "Replicate"),
		("mn_CopyObjectData", "Copy Data (Mesh)"),
		("mn_ObjectOutputNode", "Transform Output"),
		("mn_ObjectAttributeOutputNode", "Attribute Output"),
		("mn_ModifierOutputNode", "Modifier Output"),
		("mn_CopyTransformsNode", "Copy Transforms") ] ))
		
	nodes.append(("List", [
		("mn_GetListElementNode", "Get Element"),
		("mn_SetListElementNode", "Set Element"),
		("mn_GetListLengthNode", "Length"),
		("mn_CombineListsNode", "Combine"),
		("mn_ShuffleListNode", "Shuffle"),
		("mn_SumListElementsNode", "Sum Elements") ] ))
		
	nodes.append(("Sound", [
		("mn_SoundBakeNode", "Bake"),
		("mn_SoundInputNode", "Input") ] ))
		
	nodes.append(("Color", [
		("mn_ColorInputNode", "Color"),
		("mn_CombineColor", "Combine"),
		("mn_ColorMix", "Mix"),
		("mn_SetVertexColor", "Set Vertex Color") ] ))
		
	nodes.append(("Animation", [
		("mn_TimeInfoNode", "Time"),
		("mn_InterpolationNode", "Interpolation") ] ))
		
	nodes.append(("Debug", [
		("mn_DebugOutputNode", "Socket Values") ] ))
			
	nodes.append(("Material", [
		("mn_CyclesMaterialOutputNode", "Cycles Material Output"),
		("mn_ViewportColorNode" , "Viewport Color") ] ))

	nodes.append(("Convert", [
		("mn_ToStringConversion", "To Text"),
		("mn_ToFloatConversion", "To Decimal Number"),
		("mn_ToIntegerConversion", "To Integer") ] ))
		
	nodes.append(("Script", [
		("mn_ExpressionNode", "Expression") ] ))
		
	nodes.append(("System", [
		("mn_EnumerateObjectsNode", "Object Loop"),
		("mn_EnumerateObjectsStartNode", "Object Loop Start"),
		("mn_LoopNode", "Loop"),
		("mn_LoopStartNode", "Loop Start") ] ))
		
	return nodes