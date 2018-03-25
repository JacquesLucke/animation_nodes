from math import radians
from .. random cimport randomInteger

from . rule cimport RuleSet, freeRuleSet
from . symbol_string cimport SymbolString, freeSymbolString

from . apply_rules cimport applyGrammarRules
from . geometry cimport geometryFromSymbolString
from . parsing cimport parseRuleSet, parseSymbolString


def calculateLSystem(axiom, rules, generations, seed, defaults, partialRotations, limit):
    assert generations >= 0

    cdef SymbolString _axiom = parseSymbolString(axiom, defaults)
    cdef RuleSet _ruleSet = parseRuleSet(rules, defaults)

    cdef SymbolString symbols = applyGrammarRules(
        _axiom, _ruleSet, generations, randomInteger(seed),
        partialRotations, limit
    )

    freeRuleSet(&_ruleSet)
    freeSymbolString(&_axiom)

    geometryDefaults = {
        "Angle" : radians(defaults["Angle"])
    }

    vertices, edges, widths = geometryFromSymbolString(
        symbols, randomInteger(seed + 1), geometryDefaults
    )

    freeSymbolString(&symbols)

    return vertices, edges, widths