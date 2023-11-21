import prog1_include

def read_and_process_eqns(filename):
    eqn_list = prog1_include.read_eqn(filename)
    eqn_list = [prog1_include.convert_eqn(eqn) for eqn in eqn_list]
    return eqn_list

def read_and_process_left(filename):
    eqn_list = prog1_include.read_left(filename)
    eqn_list = [prog1_include.convert_eqn(eqn) for eqn in eqn_list]
    return eqn_list


input_filename = input("Please select your input file: ")
eqn_list = read_and_process_eqns(input_filename)
left = read_and_process_left(input_filename)
print(eqn_list)
print(left)