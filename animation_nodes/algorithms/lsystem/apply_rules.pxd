from . rule cimport *
from . symbol_string cimport *

cdef SymbolString applyGrammarRules(SymbolString axiom, RuleSet rules, float generations,
    int seed = ?, bint onlyPartialMoves = ?, symbolLimit = ?) except *