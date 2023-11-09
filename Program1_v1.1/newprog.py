import pandas as pd
import itertools
import sympy as sp
from quine_mccluskey.qm import QuineMcCluskey
from circuit import construct_expression, parse_line, build_expression
import re



def read_eqn(filename):
    with open(filename, 'r') as file:
        return [line.strip().split('=')[1].strip().rstrip(';') for line in file.readlines()]

def convert_eqn(eqn_str):
    # if isinstance(eqn_str, dict):
    #     eqn_str = str(list(eqn_str.values())[0])    
    str_out = eqn_str.replace('not', '~').replace('and', '&').replace('or', '|')
    # str_out = eqn_str.replace("!","~").replace('*', '&').replace('+', '|')
    return str_out

# def convert_boolean(bool_eqn_str):
#     return bool_eqn_str.replace("!","~").replace('*', '&').replace('+', '|')


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

def to_canonical_POS(eqn_str):
    expr = sp.sympify(eqn_str)
    _, maxterms, variables = _generate_minterms_or_maxterms(expr)

    pos = sp.And(*[sp.Or(*[var if not val else ~var for var, val in zip(variables, maxterm)]) for maxterm in maxterms])
    return pos

def inverse_SOP(eqn_str):
    expr = ~sp.sympify(eqn_str)
    minterms, _, variables = _generate_minterms_or_maxterms(expr)

    sop = sp.Or(*[sp.And(*[var if val else ~var for var, val in zip(variables, minterm)]) for minterm in minterms])
    return sop

def inverse_POS(eqn_str):
    expr = ~sp.sympify(eqn_str)
    _, maxterms, variables = _generate_minterms_or_maxterms(expr)

    pos = sp.And(*[sp.Or(*[var if not val else ~var for var, val in zip(variables, maxterm)]) for maxterm in maxterms])
    return pos

def literals_count(expr):
    return len(list(expr.atoms(sp.Symbol)))

def minimized_SOP(eqn_str):
    expr = sp.sympify(eqn_str)
    min_sop = sp.to_dnf(expr, True)  # True ensures a simplified form
    canonical_sop = to_canonical_SOP(eqn_str)
    saved_literals = literals_count(canonical_sop) - literals_count(min_sop)
    return min_sop, saved_literals

def minimized_POS(eqn_str):
    expr = sp.sympify(eqn_str)
    min_pos = sp.to_cnf(expr, True)  # True ensures a simplified form
    canonical_pos = to_canonical_POS(eqn_str)
    saved_literals = literals_count(canonical_pos) - literals_count(min_pos)
    return min_pos, saved_literals

def calculate_prime_implicants(eqn_str):
    expr = sp.sympify(eqn_str)
    variables = sorted(expr.free_symbols, key=str)

    truth_values = list(itertools.product([False, True], repeat=len(variables)))
    results = [expr.subs(dict(zip(variables, vals))) for vals in truth_values]
    
    minterms = [i for i, val in enumerate(results) if val]
    qm = QuineMcCluskey()
    return qm.simplify(minterms)

def calculate_essential_prime_implicants(eqn_str, prime_implicants):
    expr = sp.sympify(eqn_str)
    variables = sorted(expr.free_symbols, key=str)

    truth_values = list(itertools.product([False, True], repeat=len(variables)))
    results = [expr.subs(dict(zip(variables, vals))) for vals in truth_values]
    
    minterms = {i for i, val in enumerate(results) if val}

    essential_prime_implicants = []
    for minterm in minterms:

        covering_pis = [pi for pi in prime_implicants if all(
            pi_var == '-' or pi_var == mt_var for pi_var, mt_var in zip(pi, format(minterm, f'0{len(variables)}b')))]

        if len(covering_pis) == 1 and covering_pis[0] not in essential_prime_implicants:
            essential_prime_implicants.append(covering_pis[0])

    return essential_prime_implicants

def extract_variables_from_SOP(sop_expr):
    return sorted(list(sop_expr.free_symbols), key=lambda x: str(x))

def get_decimal_representation(minterm, variables):
    binary_list = []
    for var in variables:
        if var in minterm.args:
            binary_list.append('1')
        elif ~var in minterm.args:
            binary_list.append('0')
        else:
            binary_list.append('X') 

    binary_str = ''.join(binary_list)
    if 'X' in binary_str:  # DC cases
        all_possibilities = []
        indices = [i for i, x in enumerate(binary_str) if x == "X"]
        for combo in itertools.product('01', repeat=len(indices)):
            temp_str = list(binary_str)
            for ind, val in zip(indices, combo):
                temp_str[ind] = val
            all_possibilities.append(int(''.join(temp_str), 2))
        return all_possibilities

    return [int(binary_str, 2)]

def extract_ON_set_minterms(sop_expr):
    variables = extract_variables_from_SOP(sop_expr)
    minterms_decimal = set()

    if isinstance(sop_expr, sp.Or):
        for term in sop_expr.args:
            for val in get_decimal_representation(term, variables):
                minterms_decimal.add(val)
    else:
        for val in get_decimal_representation(sop_expr, variables):
            minterms_decimal.add(val)

    return sorted(list(minterms_decimal))

def extract_ON_set_maxterms(sop_expr):
    variables = extract_variables_from_SOP(sop_expr)
    all_possible_minterms = set(range(2**len(variables)))

    current_minterms = set(extract_ON_set_minterms(sop_expr))

    maxterms = all_possible_minterms - current_minterms

    return sorted(list(maxterms))


def write_results(filename, eqn_list,src_file):
    with open(filename, 'w') as file:
        print("File opened")
        for eqn in eqn_list:
            sop = to_canonical_SOP(eqn)
            expr_dnf = to_canonical_SOP(eqn)
            pos = to_canonical_POS(eqn)
            inv_sop = inverse_SOP(eqn)
            inv_pos = inverse_POS(eqn)
            min_sop, saved_sop_literals = minimized_SOP(eqn)
            min_pos, saved_pos_literals = minimized_POS(eqn)
            prime_implicants = calculate_prime_implicants(eqn)
            essential_prime_implicants = calculate_essential_prime_implicants(eqn, prime_implicants)  
            on_set_minterms = extract_ON_set_minterms(sop)  
            on_set_maxterms = extract_ON_set_maxterms(sop)  
            ############# truth table
            expr = sp.sympify(eqn)
            variables = sorted(expr.free_symbols, key=str)
            truth_values = list(itertools.product([False, True], repeat=len(variables)))
            results = [expr.subs(dict(zip(variables, vals))) for vals in truth_values]
            numeric_results = [1 if res is sp.true else 0 for res in results]
            ############# end truth table
            ############# transistor count
            expr_str = str(min_sop)
            count_or = expr_str.count('|')
            count_and = expr_str.count('&')
            count_not = expr_str.count('~')
            count_trans = count_or * 6 + count_and * 6 + count_not * 2
            ############# end trnasistor count

            print("\n\n-------Exporting Results--------")
            file.write(f"File source:{src_file}\n")
            #file.write(f"File type:{sel}\n")
            file.write(f"Original Equation: {eqn}\n")
            file.write(f"Canonical SOP: {sop}\n")
            file.write(f"Canonical POS: {pos}\n")
            file.write(f"Inverse SOP: {inv_sop}\n")
            file.write(f"Inverse POS: {inv_pos}\n")
            file.write(f"Minimized SOP: {min_sop}\n")
            file.write(f"Saved SOP Literals: {saved_sop_literals}\n")
            file.write(f"Minimized POS: {min_pos}\n")
            file.write(f"Saved POS Literals: {saved_pos_literals}\n")
            file.write(f"Prime Implicants: {', '.join(map(str, prime_implicants))}\n")
            file.write(f"Essential Prime Implicants: {', '.join(map(str, essential_prime_implicants))}\n")  
            file.write(f"Number of ON-Set Minterms: {len(on_set_minterms)}\n") 
            file.write(f"Number of ON-Set Maxterms: {len(on_set_maxterms)}\n") 
            file.write("-" * 40 + "\n")
            file.write("\nTruth Table:\n")
            file.write("Variables: " + ', '.join([str(v) for v in variables]) + "\n")
            file.write("-" * (25 + len(variables) * 5) + "\n")
            for vals, res in zip(truth_values, numeric_results):
                vals_as_numbers = [1 if v else 0 for v in vals]
                file.write(f"{' '.join(map(str,vals_as_numbers)):>15} : {res}\n")
            file.write("Transistor numbers needed to implement this SOP format directly with")
            file.write(f" AND, NOT, OR gates: {count_trans}\n")
            print("Export completed")


def main():
    # import os
    # print(os.getcwd())
    filename = input("Please enter the filename: ")
    try:
        with open(filename, 'r') as file:
            content = file.read()
            print(f"File content:\n{content}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
 
        
    print("Select your input type.")
    sel = input("Circuit(C) / Boolean eqn(B)\n")
    output_filename = input("Please type in the name for export file:")
    if(sel == 'b'):
        #input_filename = './Program1/input.eqn'
        #output_filename = './output.txt'
        #filetype = 'Boolean Equation'
        eqn_list = read_eqn(filename)
        eqn_list = [convert_eqn(eqn) for eqn in eqn_list]
        print(f"Your boolean equation is {eqn_list}")
        print("\n\n------Processing--------")
        write_results(output_filename, eqn_list, filename)
        print(f"Results exported to '{output_filename}")
    elif(sel == 'c'):
        eqn_str = construct_expression(filename)
        eqn_str = convert_eqn(eqn_str)
        eqn_list = [eqn_str]
        print(f"The corresponding boolean equation is {eqn_list}")
        
        
        # try:
        eqn_str = eqn_str.replace(" ", "").replace("(~","~(")
        expr = sp.sympify(eqn_str)
        print(expr)
        A, B, C, D, E, F = sp.symbols('A B C D E F')
        eqn_list = [expr]
        write_results(output_filename, eqn_list, filename)
        print(f"\n\nResults exported to '{output_filename}")
        # except Exception as e:
        #     print(f"An error occurred while converting the string to a SymPy expression: {e}")
        # return None
        
    
    else:
        print("Error")
    
if __name__ == "__main__":
    main()