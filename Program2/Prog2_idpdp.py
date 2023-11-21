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
        self.external_in = self.get_external_in_vars(original_expr) if function != "Sub-LUT Function" and function != "Combined Function" else []
        self.external_out = []  # 初始化为空

    def get_external_in_vars(self, expr):
        return sorted(set(filter(str.isalpha, expr))) if expr else []

    def add_connection(self, lut):
        self.connections.append(lut)
        if self.function == "Combined Function":
            self.internal_in.append(lut.id)  # Combined LUT 的内部输入
        elif lut.function == "Combined Function":
            self.internal_out.append(lut.id)  # Sub-LUT 的内部输出

    def display(self):
        function_str = f"Function: {self.function} | Original Expr: {self.original_expr}" if self.function == "Combined Function" else f"Function: {self.function if self.function else 'Not assigned'}"

        internal_in_str = ', '.join(f"LUT {lut_id}" for lut_id in self.internal_in) if self.internal_in else "None"
        internal_out_str = ', '.join(f"LUT {lut_id}" for lut_id in self.internal_out) if self.internal_out else "None"
        internal_connection = f"Internal Connection: IN from {internal_in_str}, OUT to {internal_out_str}"

        external_in_str = ', '.join(self.external_in) if self.external_in else "None"
        external_out_str = ', '.join(self.external_out) if self.external_out else "None"
        external_connection = f"External Connection: IN from {external_in_str}, OUT to {external_out_str}"

        return f"LUT {self.id}: Bit Width: {self.bit_width} | {function_str} | {internal_connection} | {external_connection}"

def split_equation(eqn):
    vars = sorted(set(filter(str.isalpha, eqn)))
    first_half = ''.join(vars[:4])
    second_half = ''.join(vars[4:])
    return first_half, second_half

def create_lut(eqn, lut_id, luts, external_outputs):
    bit_width = len(set(filter(str.isalpha, eqn)))
    # 获取外部输出名称（跳过 Sub-LUT）
    external_out_name = external_outputs.pop(0) if bit_width <= 6 else None

    if bit_width <= 6:  # 对于4或6变量的方程
        min_sop, _ = prog1_include.minimized_SOP(eqn)
        lut = LUT(id=lut_id, bit_width=bit_width, function=str(min_sop))
        lut.external_out = [external_out_name]
        lut.external_in = sorted(set(filter(str.isalpha, eqn)))  # 设置外部输入
        luts.append(lut)
        return lut_id + 1
    elif bit_width == 8:  # 对于8变量的方程
        eqn1, eqn2 = split_equation(eqn)
        combined_lut = LUT(id=lut_id + 2, bit_width=bit_width, function="Combined Function", original_expr=eqn)
        combined_lut.external_out = [external_outputs.pop(0)]  # 为 Combined LUT 设置外部输出

        lut1 = LUT(id=lut_id, bit_width=4, function="Sub-LUT Function", original_expr=eqn1)
        lut1.add_connection(combined_lut)
        lut1.external_in = sorted(set(filter(str.isalpha, eqn1)))  # 设置外部输入

        lut2 = LUT(id=lut_id + 1, bit_width=4, function="Sub-LUT Function", original_expr=eqn2)
        lut2.add_connection(combined_lut)
        lut2.external_in = sorted(set(filter(str.isalpha, eqn2)))  # 设置外部输入

        combined_lut.add_connection(lut1)
        combined_lut.add_connection(lut2)

        luts.extend([lut1, lut2, combined_lut])
        return lut_id + 3

    return lut_id + 1

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

def print_lut_table(luts):
    # 打印表头
    print("{:<8} | {:<30} | {:<30}".format("LUT ID", "Internal Connection", "External Connection"))
    print("-" * 70)  # 分隔线

    # 遍历所有 LUTs 打印信息
    for lut in luts:
        internal_conn = "IN from " + ', '.join(f"LUT {lut_id}" for lut_id in lut.internal_in if lut.internal_in) 
        internal_conn += " | OUT to " + ', '.join(f"LUT {lut_id}" for lut_id in lut.internal_out if lut.internal_out)
        internal_conn = internal_conn if internal_conn.strip() else "None"

        external_conn = "IN from " + ', '.join(lut.external_in) if lut.external_in else "None"
        external_conn += " | OUT to " + ', '.join(lut.external_out) if lut.external_out else "None"

        print("{:<8} | {:<30} | {:<30}".format("LUT " + str(lut.id), internal_conn, external_conn))

def generate_lut_bitstream(lut):
    internal_in_str = ', '.join(f"LUT {lut_id}" for lut_id in lut.internal_in) if lut.internal_in else "None"
    internal_out_str = ', '.join(f"LUT {lut_id}" for lut_id in lut.internal_out) if lut.internal_out else "None"
    internal_conn_str = f"IC{internal_in_str}/{internal_out_str}"

    external_in_str = ''.join(lut.external_in) if lut.external_in else "None"
    external_out_str = ''.join(lut.external_out) if lut.external_out else "None"
    external_conn_str = f"EC{external_in_str}/{external_out_str}"

    bitstream = f"L{lut.id}{internal_conn_str}{external_conn_str}"
    return bitstream

def parse_bitstream(bitstream):
    # 解析比特流，创建并返回一个 LUT 对象
    lut_id = bitstream.split('L')[1].split('IC')[0]
    internal_conn_str = bitstream.split('IC')[1].split('EC')[0]
    external_conn_str = bitstream.split('EC')[1]
    
    internal_in = [x.strip() for x in internal_conn_str.split('/')[0].split(',')] if '/' in internal_conn_str else []
    internal_out = [x.strip() for x in internal_conn_str.split('/')[1].split(',')] if '/' in internal_conn_str else []
    
    external_in = [x.strip() for x in external_conn_str.split('/')[0].split(',')] if '/' in external_conn_str else []
    external_out = [x.strip() for x in external_conn_str.split('/')[1].split(',')] if '/' in external_conn_str else []
    
    # 创建一个 LUT 对象
    lut = LUT(lut_id, None)  # bit_width 在此处未知
    lut.internal_in = internal_in
    lut.internal_out = internal_out
    lut.external_in = external_in
    lut.external_out = external_out

    return lut

def process_txt_file(filename):
    luts = []
    with open(filename, 'r') as file:
        for line in file:
            lut = parse_bitstream(line.strip())
            luts.append(lut)
    return luts

def calculate_memory_usage(luts):
    memory = 0
    for lut in luts:
        if lut.bit_width == 4 or lut.function == "Combined Function":
            memory += 16  # 4-bit LUT 或者 Combined Function LUT
        elif lut.bit_width == 6:
            memory += 64  # 6-bit LUT
        # 如果有其他 bit_width 的情况，可以在此处添加
    return memory / 8  # 将 bit 转换为 Byte


def calculate_summary(luts):
    total_luts = len(luts)
    total_internal_connections = sum(len(lut.internal_in) + len(lut.internal_out) for lut in luts)
    max_internal_connections = total_luts * (total_luts - 1)  # 理论上每个 LUT 可以与其他所有 LUT 连接

    lut_usage = f"{total_luts} LUTs used"
    internal_connection_usage = f"{(total_internal_connections / max_internal_connections) * 100:.2f}% of internal connections used"
    memory_usage = f"{calculate_memory_usage(luts)} Bytes of memory required"

    return lut_usage, internal_connection_usage, memory_usage

# 主程序
input_filename = input("Please select your input file: ")

if input_filename.endswith('.eqn'):
    eqn_list = read_and_process_eqns(input_filename)

    luts = []  # 用于存储LUT对象的列表
    lut_id = 0
    # 生成外部输出名称列表
    external_outputs = [chr(ord('Z') - i) for i in range(len(eqn_list))]
    external_outputs_backup = external_outputs.copy()

    for eqn in eqn_list:
        lut_id = create_lut(eqn, lut_id, luts, external_outputs)

    # 收集并打印所有变量
    all_vars = get_all_variables(eqn_list)
    print("External input:", ", ".join(all_vars))

    # 打印所有外部输出
    print("External output:", ", ".join(external_outputs_backup[:len(luts)]))

    # 打印所有 LUT 信息
    for lut in luts:
        print(lut.display())

    print_lut_table(luts)

    # 生成比特流并写入文件
    bitstreams = [generate_lut_bitstream(lut) for lut in luts]
    with open('bitstream.txt', 'w') as file:
        for bitstream in bitstreams:
            file.write(bitstream + '\n')

elif input_filename.endswith('.txt'):
    luts = process_txt_file(input_filename)
    print_lut_table(luts)

if input_filename.endswith('.eqn'):
    # ...（处理 .eqn 文件的代码）
    summary = calculate_summary(luts)
    print("\nSummary:")
    print("\n".join(summary))