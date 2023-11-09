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


# try:
#     expression = construct_expression('circuit.txt')
#     print(expression)
# except KeyError as e:
#     print(e)
    
    
    
# def circuit(filename):
#     with open(filename, 'r') as file:
#         lines = file.readlines()

#     parsed_expressions = []
#     defined_symbols = set()

#     for line in lines:
#         line = line.strip()
#         parts = re.split(r'[\s,()]+', line)[1:-1]
#         if line.startswith('not'):
#             #parts = re.split(r'[\s,()]+', line)[1:-1]
#             if len(parts) == 2:  
#                 dest, src = parts
#                 defined_symbols.add(dest)
#                 #parsed_expressions.append(f"{dest} = ~{src}")
#                 not_expr = f"~{src}"
#                 try:
#                     #sp.sympify(not_expr)
#                     rhs_expr = sp.sympify(f"~{src}")
#                     parsed_expressions.append({dest: rhs_expr}) 
#                 except sp.SympifyError as e:
#                     print(f"Error in parsing NOT expression: {rhs_expr}. Error: {e}")
#             else:
#                 print("Error: Incorrect syntax for NOT operation.")

#         elif line.startswith('out'):
#             if len(parts) == 1:
#                 dest
                
                
#         elif line.startswith('and'):
#             if len(parts) == 3:  
#                 dest, src1, src2 = parts
#                 defined_symbols.add(dest)
#                 and_expr = f"{src1} & {src2}"
#                 try:
#                     #sp.sympify(and_expr)
#                     rhs_expr = sp.sympify(f"{src1} & {src2}")
#                     #parsed_expressions.append(f"{dest} = {rhs_expr}")
#                     parsed_expressions.append({dest: rhs_expr}) 
#                 except sp.SympifyError as e:
#                     print(f"Error in parsing AND expression: {and_expr}. Error: {e}")
#             else:
#                 print(f"Error: Incorrect syntax in AND operation: {line}")

#         elif line.startswith('or'):
#             if len(parts) == 3:  
#                 dest, src1, src2 = parts
#                 defined_symbols.add(dest)
#                 or_expr = f"{src1} | {src2}"
#                 try:
#                     #sp.sympify(or_expr)
#                     rhs_expr = sp.sympify(f"{src1} | {src2}")
#                     #parsed_expressions.append(f"{dest} = {rhs_expr}")
#                     parsed_expressions.append({dest: rhs_expr}) 
#                 except sp.SympifyError as e:
#                     print(f"Error in parsing OR expression: {or_expr}. Error: {e}")
#             else:
#                 print(f"Error: Incorrect syntax in OR operation: {line}")
#     return parsed_expressions

# def circuit(filename):
#     with open(filename, 'r') as file:
#         lines = file.readlines()

#     parsed_expressions = {}
#     defined_symbols = set()

#     for line in lines:
#         line = line.strip()
#         parts = re.split(r'[\s,()]+', line)[1:-1]

#         op, dest = parts[0], parts[1]
#         defined_symbols.add(dest)

#         if op == 'not' and len(parts) == 3:  
#             src = parts[2]
#             parsed_expressions[dest] = f"~{src}"

#         elif op == 'and' and len(parts) == 4:
#             src1, src2 = parts[2], parts[3]
#             parsed_expressions[dest] = f"({src1} & {src2})"

#         elif op == 'or' and len(parts) == 4:
#             src1, src2 = parts[2], parts[3]
#             parsed_expressions[dest] = f"({src1} | {src2})"
#         else:
#             print(f"Error: Incorrect syntax in line: {line}")
#             continue

#     if 'out' not in parsed_expressions:
#         print("Error: 'out' operation not found in the input.")
#         return None
#     # Generate the final expression by recursively replacing variables
#     final_expr = parsed_expressions['out']
#     while any(var in final_expr for var in defined_symbols):
#         for var, expr in parsed_expressions.items():
#             final_expr = final_expr.replace(var, f"({expr})")
#     return final_expr
