def getNodeNameDictionary():
	nodes = []
	
	nodes.append(("Number", [
		"mn_FloatInputNode",
		"mn_IntegerInputNode",
		"mn_FloatListInputNode",
		"mn_RandomNumberNode",
		"mn_PerlinNoise1D",
		"mn_FloatMathNode" ] ))
		
	nodes.append(("Vector", [
		"mn_CombineVector",
		"mn_SeparateVector",
		"mn_VectorLengthNode" ] ))	
		
	nodes.append(("Text", [
		"mn_StringInputNode",
		"mn_StringListInputNode",
		"mn_RandomStringNode",
		"mn_CharactersNode",
		"mn_CombineStringsNode",
		"mn_ReplicateStringsNode",
		"mn_SubstringNode",
		"mn_StringAnalyzeNode",
		"mn_TextOutputNode" ] ))
	
	nodes.append(("Object", [
		"mn_ObjectInputNode",
		"mn_ObjectListInputNode",
		"mn_ObjectInfoNode",
		"mn_ReplicateObjectNode",
		"mn_ObjectOutputNode",
		"mn_ObjectAttributeOutputNode",
		"mn_ModifierOutputNode",
		"mn_CopyTransformsNode"] ))
		
	nodes.append(("List", [
		"mn_GetListElementNode",
		"mn_GetListLengthNode",
		"mn_SetListElementNode",
		"mn_SumListElementsNode",
		"mn_CombineListsNode",
		"mn_ShuffleListNode" ] ))
		
	nodes.append(("Sound", [
		"mn_SoundBakeNode",
		"mn_SoundInputNode" ] ))
		
	nodes.append(("Color", [
		"mn_ColorInputNode" ] ))
		
	nodes.append(("Animation", [
		"mn_TimeInfoNode" ] ))
		
	nodes.append(("Debug", [
		"mn_DebugOutputNode" ] ))
			
	nodes.append(("Material", [
		"mn_MaterialOutputNode" ] ))

	nodes.append(("Convert", [
		"mn_ToStringConversion",
		"mn_ToFloatConversion",
		"mn_ToIntegerConversion" ] ))
		
	nodes.append(("Script", [
		"mn_ExpressionNode" ] ))
		
	nodes.append(("System", [
		"mn_LoopNode",
		"mn_LoopStartNode",
		"mn_EnumerateObjectsStartNode",
		"mn_EnumerateObjectsNode" ] ))
		
	return nodes