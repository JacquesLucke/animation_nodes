from math import radians
from .. random cimport randomInteger

from . rule cimport RuleSet, freeRuleSet
from . symbol_string cimport SymbolString, freeSymbolString, LSystemSymbolString

from . apply_rules cimport applyGrammarRules
from . geometry cimport geometryFromSymbolString
from . parsing cimport parseRuleSet, parseSymbolString


def calculateLSystem(axiom, rules, generations, seed, defaults, onlyPartialMoves = True, limit = None):
    assert generations >= 0

    cdef SymbolString _axiom = parseSymbolString(axiom, defaults)
    cdef RuleSet _ruleSet = parseRuleSet(rules, defaults)

    cdef SymbolString symbols = applyGrammarRules(
        _axiom, _ruleSet, generations, randomInteger(seed),
        onlyPartialMoves, limit
    )

    freeRuleSet(&_ruleSet)
    freeSymbolString(&_axiom)

    geometryDefaults = {
        "Angle" : radians(defaults["Angle"])
    }

    vertices, edges, widths, statesJ, statesK, statesM = geometryFromSymbolString(
        symbols, randomInteger(seed + 1), geometryDefaults
    )

    outputSymbols = LSystemSymbolString.fromSymbolString(symbols)

    return vertices, edges, widths, outputSymbols, statesJ, statesK, statesM