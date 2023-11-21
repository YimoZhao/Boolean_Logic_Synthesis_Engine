import prog1_include

class LUT:
    def __init__(self, id, bit_width, function=None, original_expr=None):
        self.id = id
        self.bit_width = bit_width
        self.function = function
        self.original_expr = original_expr
        self.connections = []
        self.internal_in = []  # 内部输入连接
        self.internal_out = []  # 内部输出连接
        # 设置外部输入和输出
        self.external_in = self.get_external_in_vars(original_expr) if function != "Sub-LUT Function" and function != "Combined Function" else []
        self.external_out = self.get_external_out_vars(function, id)

    def get_external_in_vars(self, expr):
        return sorted(set(filter(str.isalpha, expr))) if expr else []

    def get_external_out_vars(self, function, id):
        if function == "Sub-LUT Function":
            return []  # Sub-LUT 没有外部输出
        # 生成外部输出名称，例如 'Z', 'Y', 'X', ...
        return [chr(ord('Z') - id % 26)]

    def get_external_in_vars(self, expr):
        return sorted(set(filter(str.isalpha, expr))) if expr else []
    
    def add_connection(self, lut):
        self.connections.append(lut)
        if self.function == "Combined Function":
            self.internal_in.append(lut.id)  # Combined LUT 的内部输入
        elif lut.function == "Combined Function":
            self.internal_out.append(lut.id)  # Sub-LUT 的内部输出

    def get_output_name(self, output_id):
        return chr(ord('Z') - output_id % 26)

    def get_external_output_name(self, output_id):
        if output_id is not None and self.function != "Sub-LUT Function":
            return self.get_output_name(output_id)
        return None

    def display(self, external_output_id=None):
        function_str = f"Function: {self.function} | Original Expr: {self.original_expr}" if self.function == "Combined Function" else f"Function: {self.function if self.function else 'Not assigned'}"

        internal_in_str = ', '.join(f"LUT {lut_id}" for lut_id in self.internal_in) if self.internal_in else "None"
        internal_out_str = ', '.join(f"LUT {lut_id}" for lut_id in self.internal_out) if self.internal_out else "None"
        internal_connection = f"Internal Connection: IN from {internal_in_str}, OUT to {internal_out_str}"

        external_in_str = ', '.join(self.external_in) if self.external_in else "None"
        external_out_str = ', '.join(self.external_out) if self.external_out else "None"
        external_connection = f"External Connection: IN from {external_in_str}, OUT to {external_out_str}"

        return f"LUT {self.id}: Bit Width: {self.bit_width} | {function_str} | {internal_connection} | {external_connection}"


def split_equation(eqn):
    # 分割逻辑可能需要调整以适应具体方程
    # 假设 eqn 是一个字符串，包含八个不同的变量
    vars = sorted(set(filter(str.isalpha, eqn)))
    first_half = ''.join(vars[:4])
    second_half = ''.join(vars[4:])
    return first_half, second_half

def create_lut(eqn, lut_id, luts, external_outputs):
    bit_width = len(set(filter(str.isalpha, eqn)))
    external_out_name = external_outputs.pop(0) if bit_width <= 6 else None

    if bit_width <= 6:  # 对于4或6变量的方程
        min_sop, _ = prog1_include.minimized_SOP(eqn)
        lut = LUT(id=lut_id, bit_width=bit_width, function=str(min_sop), original_expr=eqn)
        lut.external_out = [external_out_name]
        lut.external_in = sorted(set(filter(str.isalpha, eqn)))  # 正确设置外部输入
        luts.append(lut)
    elif bit_width == 8:  # 对于8变量的方程
        eqn1, eqn2 = split_equation(eqn)
        combined_lut = LUT(id=lut_id + 2, bit_width=bit_width, function="Combined Function", original_expr=eqn)
        combined_lut.external_out = [external_outputs.pop(0)]  # 为 Combined LUT 设置外部输出

        lut1 = LUT(id=lut_id, bit_width=4, function="Sub-LUT Function", original_expr=eqn1)
        lut1.add_connection(combined_lut)
        lut1.external_in = sorted(set(filter(str.isalpha, eqn1)))  # 为 Sub-LUT 设置外部输入

        lut2 = LUT(id=lut_id + 1, bit_width=4, function="Sub-LUT Function", original_expr=eqn2)
        lut2.add_connection(combined_lut)
        lut2.external_in = sorted(set(filter(str.isalpha, eqn2)))  # 为 Sub-LUT 设置外部输入

        combined_lut.add_connection(lut1)
        combined_lut.add_connection(lut2)

        luts.extend([lut1, lut2, combined_lut])
    return lut_id + (3 if bit_width == 8 else 1)


def read_and_process_eqns(filename):
    eqn_list = prog1_include.read_eqn(filename)
    eqn_list = [prog1_include.convert_eqn(eqn) for eqn in eqn_list]
    return eqn_list

def get_all_variables(eqn_list):
    all_vars = set()
    for eqn in eqn_list:
        vars_in_eqn = set(filter(str.isalpha, eqn))
        all_vars.update(vars_in_eqn)
    return sorted(all_vars)
# 主程序
input_filename = input("Please select your input file: ")
eqn_list = read_and_process_eqns(input_filename)

luts = []  # 用于存储LUT对象的列表
lut_id = 0
for eqn in eqn_list:
    lut_id = create_lut(eqn, lut_id, luts)

# 收集并打印所有变量
all_vars = get_all_variables(eqn_list)
print("External input:", ", ".join(all_vars))

# 在主程序末尾添加外部输出的打印
output_id = 0
print("External output:", end=" ")
for lut in luts:
    if lut.function != "Sub-LUT Function":
        print(lut.get_output_name(output_id), end=", ")
        output_id += 1
print()

# 仅保留此处的打印，包含外部输出信息
output_id = 0
for lut in luts:
    print(lut.display(external_output_id=output_id))
    if lut.function != "Sub-LUT Function":
        output_id += 1
