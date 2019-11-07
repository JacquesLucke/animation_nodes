from . symbol_string cimport SymbolString, freeSymbolString
from .. random cimport randomFloat_Positive
from cpython cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from libc.string cimport memset

cdef enum:
    RULE_HAS_PROBABILITY = 1
    RULE_HAS_CONDITION = 2

ctypedef bint (*RuleConditionFunction)(RuleConditionData data, void *command)

cdef struct RuleConditionData:
    unsigned char id

cdef struct RuleCondition:
    RuleConditionFunction function
    RuleConditionData data

cdef struct Rule:
    unsigned char symbol
    unsigned char flags
    float probability
    RuleCondition condition
    SymbolString replacement

cdef struct RuleSet:
    Rule **rules
    unsigned char *lengths

cdef enum RuleResultType:
    Replaced
    CanChange
    WillNotChange


cdef inline RuleResultType getReplacement(SymbolString **replacement, RuleSet *ruleSet, unsigned char symbol, void *command, int seed):
    if ruleSet.lengths[symbol] == 0:
        return RuleResultType.WillNotChange

    cdef Py_ssize_t i
    cdef Rule *rule
    cdef float randomNumber
    cdef bint probabilityFailed = False
    for i in range(ruleSet.lengths[symbol]):
        rule = ruleSet.rules[symbol] + i

        if rule.flags & RULE_HAS_CONDITION:
            if not rule.condition.function(rule.condition.data, command):
                continue

        if rule.flags & RULE_HAS_PROBABILITY:
            randomNumber = randomFloat_Positive(seed + i)
            if randomNumber > rule.probability:
                probabilityFailed = True
                continue

        replacement[0] = &rule.replacement
        return RuleResultType.Replaced
    else:
        if probabilityFailed:
            return RuleResultType.CanChange
        else:
            return RuleResultType.WillNotChange

cdef inline initRule(Rule *rule):
    memset(rule, 0, sizeof(Rule))

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