from . symbol_string cimport SymbolString, freeSymbolString
from .. random cimport randomFloat_Positive
from cpython cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from libc.string cimport memset

cdef struct Rule:
    unsigned char symbol
    unsigned char hasProbability
    float probability
    SymbolString replacement

cdef struct RuleSet:
    Rule **rules
    unsigned char *lengths

cdef inline SymbolString *getReplacement(RuleSet *ruleSet, unsigned char symbol, int seed):
    cdef Py_ssize_t i
    cdef Rule *rule
    cdef float randomNumber
    for i in range(ruleSet.lengths[symbol]):
        rule = ruleSet.rules[symbol] + i
        if rule.hasProbability:
            randomNumber = randomFloat_Positive(seed+i)
            if randomNumber < rule.probability:
                return &rule.replacement
        else:
            return &rule.replacement
    else:
        return NULL

cdef inline initRuleSet(RuleSet *ruleSet):
    ruleSet.rules = <Rule**>PyMem_Malloc(256 * sizeof(Rule*))
    memset(ruleSet.rules, 0, 256 * sizeof(Rule*))

    ruleSet.lengths = <unsigned char*>PyMem_Malloc(256 * sizeof(unsigned char))
    memset(ruleSet.lengths, 0, 256 * sizeof(unsigned char))

cdef inline freeRuleSet(RuleSet *ruleSet):
    cdef Py_ssize_t symbol, j
    for symbol in range(256):
        for j in range(ruleSet.lengths[symbol]):
            freeRule(&ruleSet.rules[symbol][j])
        if ruleSet.lengths[symbol] > 0:
            PyMem_Free(ruleSet.rules[symbol])
    PyMem_Free(ruleSet.rules)
    PyMem_Free(ruleSet.lengths)

cdef inline freeRule(Rule *rule):
    freeSymbolString(&rule.replacement)