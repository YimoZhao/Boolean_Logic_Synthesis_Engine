import prog1_include

# LUT类定义
class LUT:
    def __init__(self, id, max_inputs, function=None):
        self.id = id
        self.max_inputs = max_inputs
        self.function = function
        self.connections = []

    def assign_function(self, function):
        self.function = function

    def add_connection(self, lut):
        self.connections.append(lut)

    def display(self):
        connected_to = ', '.join(str(lut.id) for lut in self.connections)
        return f"LUT {self.id}: Function: {self.function if self.function else 'Not assigned'} | Connected to: [{connected_to}]"

# 最小SOP程序的核心部分
def read_and_process_eqns(filename):
    eqn_list = prog1_include.read_eqn(filename)
    eqn_list = [prog1_include.convert_eqn(eqn) for eqn in eqn_list]
    return eqn_list

def process_eqn(eqn):
    if prog1_include.false_detect(eqn):
        return None
    else:
        min_sop, _ = prog1_include.minimized_SOP(eqn)
        return str(min_sop)

# 主程序
input_filename = input("Please select your input file: ")
eqn_list = read_and_process_eqns(input_filename)

luts = []  # 用于存储LUT对象的列表
for i, eqn in enumerate(eqn_list):
    minimized_sop = process_eqn(eqn)
    if minimized_sop is not None:
        lut = LUT(id=i, max_inputs=len(eqn), function=minimized_sop)
        luts.append(lut)

# 打印所有LUT
for lut in luts:
    print(lut.display())
