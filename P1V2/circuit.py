import re
import sympy as sp

def parse_line(line):
    parts = re.split(r'[\s,()]+', line)
    operation, operands = parts[0], parts[1:]
    return operation, operands

def build_expression(expressions, var):
    if var not in expressions:  # var define
        return var
    
    operation, operands = expressions[var]
    
    if operation == 'not':
        return f"~({build_expression(expressions, operands[0])})"
    elif operation == 'and':
        return f"({build_expression(expressions, operands[0])} & {build_expression(expressions, operands[1])})"
    elif operation == 'or':
        return f"({build_expression(expressions, operands[0])} | {build_expression(expressions, operands[1])})"
    elif operation == 'out':  # Handling the 'out' operation
        return build_expression(expressions, operands[0])
    else:
        return f"Error: Incorrect syntax in {var}"

def construct_expression(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    expressions = {}
    for line in lines:
        operation, operands = parse_line(line.strip())
        if operation == 'out': 
            expressions['out'] = ('out', operands)
        else:
            dest_var = operands[0] 
            expressions[dest_var] = (operation, operands[1:])

    return build_expression(expressions, 'out')