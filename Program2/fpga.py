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


sram_values = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0]
lut0 = LUT4(sram_values)

###
output = lut0.compute([1, 1, 1, 0])
print(output)
###

