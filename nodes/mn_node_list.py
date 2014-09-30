def getNodeNameDictionary():
	nodes = []
	
	nodes.append(("Input", [
		"IntegerInputNode",
		"FloatInputNode",
		"StringInputNode",
		"ObjectInputNode",
		"TimeInfoNode",
		"ObjectInfoNode",
		"RandomNumberNode",
		"RandomStringNode",
		"CharactersNode" ] ))
		
	nodes.append(("Output", [
		"TextOutputNode",
		"ObjectOutputNode",
		"AttributeOutputNode",
		"DebugOutputNode" ] ))
		
	nodes.append(("Strings", [
		"CombineStringsNode",
		"ReplicateStringsNode",
		"SubstringNode",
		"StringLengthNode" ] ))

	nodes.append(("Convert", [
		"ToStringConversion",
		"ToFloatConversion",
		"ToIntegerConversion",
		"CombineVector",
		"SeparateVector" ] ))
	
	nodes.append(("Math", [
		"FloatMathNode" ] ))
		
	nodes.append(("Script", [
		"ExpressionNode" ] ))
	
	return nodes