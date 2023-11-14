import prog1_include
import itertools
import sympy as sp


input_filename = input("Please select your input file")
eqn_list = prog1_include.read_eqn(input_filename)
eqn_list = [prog1_include.convert_eqn(eqn) for eqn in eqn_list]
print(f"Your boolean equation is {eqn_list}")
intermediate_file = input("Please select your intermediate file")

for eqn in eqn_list:
    with open(intermediate_file,'w') as file:
        if prog1_include.false_detect(eqn):                
                print("\n\n-------Exporting Results--------")
                file.write(f"File source:{input_filename}\n")
                #file.write(f"File type:{sel}\n")
                file.write(f"Original Equation: {eqn}\n")
                file.write(f"Equation is always False\n")
                #false logic
        else:
            min_sop, saved_sop_literals = prog1_include.minimized_SOP(eqn)
            print("\n\n-------Exporting Results--------")
            file.write(f"Minimized SOP: {min_sop}\n")