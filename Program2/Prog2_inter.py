import intersop as ip
import sympy as sp

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
    # 使用 Sympy 解析方程式，并获取方程式中的所有符号（变量）
    symbols = sp.sympify(eqn).free_symbols
    # 转换符号为字符串，并筛选出由字母组成的字符串
    bit_width = len({str(symbol) for symbol in symbols if str(symbol).isalpha()})

    external_out_name = external_outputs.pop(0) if bit_width <= 6 else None

    if bit_width <= 6:
        min_sop, _ = ip.minimized_SOP(eqn)
        lut = LUT(id=lut_id, bit_width=bit_width, function=str(min_sop))
        lut.external_out = [external_out_name]
        lut.external_in = sorted({str(symbol) for symbol in symbols if str(symbol).isalpha()})
        luts.append(lut)
        return lut_id + 1
    elif bit_width == 8:
        eqn1, eqn2 = split_equation(eqn)
        combined_lut = LUT(id=lut_id + 2, bit_width=bit_width, function="Combined Function", original_expr=eqn)
        combined_lut.external_out = [external_outputs.pop(0)]

        lut1 = LUT(id=lut_id, bit_width=4, function="Sub-LUT Function", original_expr=eqn1)
        lut1.add_connection(combined_lut)
        lut1.external_in = sorted({str(symbol) for symbol in sp.sympify(eqn1).free_symbols if str(symbol).isalpha()})

        lut2 = LUT(id=lut_id + 1, bit_width=4, function="Sub-LUT Function", original_expr=eqn2)
        lut2.add_connection(combined_lut)
        lut2.external_in = sorted({str(symbol) for symbol in sp.sympify(eqn2).free_symbols if str(symbol).isalpha()})

        combined_lut.add_connection(lut1)
        combined_lut.add_connection(lut2)

        luts.extend([lut1, lut2, combined_lut])
        return lut_id + 3

    return lut_id + 1

def read_and_process_eqns(filename):
    eqn_list = ip.read_eqn(filename)
    eqn_list = [ip.convert_eqn(eqn) for eqn in eqn_list.values()]
    return eqn_list

def get_all_variables(eqn_list):
    all_vars = set()
    for eqn in eqn_list:
        # 使用 sympify 将字符串方程式转换为 Sympy 表达式
        expr = sp.sympify(eqn)

        # 从表达式中提取所有符号（变量）
        symbols = expr.free_symbols

        # 将符号转换为字符串并检查它是否是由字母组成
        for symbol in symbols:
            symbol_str = str(symbol)
            if symbol_str.isalpha():
                all_vars.add(symbol_str)

    return sorted(all_vars)



def print_lut_table(luts):
    print("{:<8} | {:<30} | {:<30}".format("LUT ID", "Internal Connection", "External Connection"))
    print("-" * 70)

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
    lut_id = bitstream.split('L')[1].split('IC')[0]
    internal_conn_str = bitstream.split('IC')[1].split('EC')[0]
    external_conn_str = bitstream.split('EC')[1]
    
    internal_in = [x.strip() for x in internal_conn_str.split('/')[0].split(',')] if '/' in internal_conn_str else []
    internal_out = [x.strip() for x in internal_conn_str.split('/')[1].split(',')] if '/' in internal_conn_str else []
    
    external_in = [x.strip() for x in external_conn_str.split('/')[0].split(',')] if '/' in external_conn_str else []
    external_out = [x.strip() for x in external_conn_str.split('/')[1].split(',')] if '/' in external_conn_str else []
    
    lut = LUT(lut_id, None)
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
            memory += 16
        elif lut.bit_width == 6:
            memory += 64
    return memory / 8

def calculate_summary(luts):
    total_luts = len(luts)
    total_internal_connections = sum(len(lut.internal_in) + len(lut.internal_out) for lut in luts)
    max_internal_connections = total_luts * (total_luts - 1)

    lut_usage = f"{total_luts} LUTs used"
    internal_connection_usage = f"{(total_internal_connections / max_internal_connections) * 100:.2f}% of internal connections used"
    memory_usage = f"{calculate_memory_usage(luts)} Bytes of memory required"

    return lut_usage, internal_connection_usage, memory_usage

# 主程序
input_filename = input("Please select your input file: ")

if input_filename.endswith('.eqn'):
    eqn_dict = ip.read_eqn(input_filename)

    luts = []  # 用于存储LUT对象的列表
    lut_id = 0
    external_outputs = [var for var in eqn_dict.keys()]
    external_outputs_backup = external_outputs.copy()

    for var, eqn in eqn_dict.items():
        simplified_eqn = ip.minimized_SOP(eqn)
        lut_id = create_lut(simplified_eqn, lut_id, luts, external_outputs)

    all_vars = get_all_variables([eqn for eqn in eqn_dict.values()])
    print("External input:", ", ".join(all_vars))

    print("External output:", ", ".join(external_outputs_backup[:len(luts)]))

    for lut in luts:
        print(lut.display())

    print_lut_table(luts)

    bitstreams = [generate_lut_bitstream(lut) for lut in luts]
    with open('bitstream.txt', 'w') as file:
        for bitstream in bitstreams:
            file.write(bitstream + '\n')

elif input_filename.endswith('.txt'):
    luts = process_txt_file(input_filename)
    print_lut_table(luts)

if input_filename.endswith('.eqn'):
    summary = calculate_summary(luts)
    print("\nSummary:")
    print("\n".join(summary))