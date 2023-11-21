import pandas as pd
import itertools
import sympy as sp
from sympy import symbols, simplify_logic, S

def read_eqn(filename):
    eqns = {}
    with open(filename, 'r') as file:
        for line in file:
            left, right = [side.strip() for side in line.strip().split('=')]
            eqns[left] = right
    return eqns

def false_detect(expr_str):
    expr = sp.sympify(expr_str)
    simplified_expr = simplify_logic(expr)
    return simplified_expr == S.false

def convert_eqn(eqn_str):
    str_out = eqn_str.replace('not', '~').replace('and', '&').replace('or', '|')
    return str_out

def _generate_minterms_or_maxterms(expr):
    variables = sorted(list(expr.free_symbols), key=lambda x: str(x))
    truth_values = list(itertools.product([False, True], repeat=len(variables)))
    results = [expr.subs(dict(zip(variables, vals))) for vals in truth_values]

    minterms = [vals for vals, res in zip(truth_values, results) if res is sp.true]
    maxterms = [vals for vals, res in zip(truth_values, results) if res is sp.false]
    return minterms, maxterms, variables

def to_canonical_SOP(eqn_str):
    expr = sp.sympify(eqn_str)
    minterms, _, variables = _generate_minterms_or_maxterms(expr)
    sop = sp.Or(*[sp.And(*[var if val else ~var for var, val in zip(variables, minterm)]) for minterm in minterms])
    return sop

def literals_count(expr):
    return len(list(expr.atoms(sp.Symbol)))

def minimized_SOP(eqn_str):
    expr = sp.sympify(eqn_str)
    min_sop = sp.to_dnf(expr, True)  # True ensures a simplified form
    canonical_sop = to_canonical_SOP(eqn_str)
    saved_literals = literals_count(canonical_sop) - literals_count(min_sop)
    return min_sop, saved_literals
