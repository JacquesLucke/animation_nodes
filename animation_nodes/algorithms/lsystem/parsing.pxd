from . rule cimport Rule, RuleSet
from . symbol_string cimport SymbolString

cdef SymbolString parseSymbolString(str source, dict defaults) except *
cdef RuleSet parseRuleSet(ruleStrings, defaults) except *