
class LUT4:
    def __init__(self, sram_values):
        if len(sram_values) != 16:
            raise ValueError("SRAM must have exactly 16 values.")
        self.sram = sram_values

    def compute(self, inputs):
        if len(inputs) != 4:
            raise ValueError("LUT4 requires exactly 4 input values.")
        input_index = int("".join(['1' if i else '0' for i in inputs]), 2)
        return self.sram[input_index]
    
    def lut_input(self, input_reg):
        return self.signal

class Crossbar:
    def __init__(self, num_inputs, num_outputs):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.switch_matrix = [[0 for _ in range(num_outputs)] for _ in range(num_inputs)]

    def connect(self, input_index, output_index):
        self.switch_matrix[input_index][output_index] = 1

    def disconnect(self, input_index, output_index):
        self.switch_matrix[input_index][output_index] = 0

    def is_connected(self, input_index, output_index):
        return self.switch_matrix[input_index][output_index]

# Redefine the PartiallyConnectedFPGA class
class PartiallyConnectedFPGA:
    def __init__(self, num_luts, num_inputs, num_outputs):
        self.luts = [LUT4([0] * 16) for _ in range(num_luts)]
        self.crossbar = Crossbar(num_inputs, num_outputs)

    def set_lut_sram(self, lut_index, sram_values):
        if lut_index >= len(self.luts):
            raise ValueError("LUT index out of range.")
        self.luts[lut_index] = LUT4(sram_values)
    


    def connect_luts(self, input_lut_index, output_lut_index):
        if input_lut_index >= len(self.luts) or output_lut_index >= len(self.luts):
            raise ValueError("LUT index out of range.")
        self.crossbar.connect(input_lut_index, output_lut_index)

    def compute(self, lut_inputs):
        if len(lut_inputs) != len(self.luts):
            raise ValueError("Input list length must match the number of LUTs.")
        lut_outputs = [self.luts[i].compute(lut_inputs[i]) for i in range(len(self.luts))]
        crossbar_outputs = [0] * len(self.luts)
        for i in range(self.crossbar.num_inputs):
            for j in range(self.crossbar.num_outputs):
                if self.crossbar.is_connected(i, j):
                    crossbar_outputs[j] = lut_outputs[i]
        return crossbar_outputs

fpga = PartiallyConnectedFPGA(4, 4, 4)
"""
fpga.set_lut_sram(n, minterm_out)
"""
fpga.set_lut_sram(0, [1, 0] * 8)
fpga.set_lut_sram(1, [0, 1] * 8)
fpga.set_lut_sram(2, [1] * 8 + [0] * 8)
fpga.set_lut_sram(3, [0] * 8 + [1] * 8)

# Connect some LUTs
fpga.connect_luts(0, 1)
fpga.connect_luts(2, 3)

# Compute the outputs with some inputs for the LUTs
#out = fpga.compute(LUT4.lut_input()) #返回[a,b,c,d]/[a,1,c,d] 也就是敏感度列表

#outputs = fpga.compute([[1, 1, 1, 1], [0, 0, 0, 0], 
#                        [1, 0, 1, 0], [0, 1, 0, 1]])

outputs = fpga.compute([[1, 1, 1, 1]]*4)

#inputs = LUT4.lut_input()
print(outputs)
#print(inputs)

