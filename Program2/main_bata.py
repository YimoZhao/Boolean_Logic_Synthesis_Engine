import prog1_include

def read_and_process_eqns(filename):
    eqn_list = prog1_include.read_eqn(filename)
    eqn_list = [prog1_include.convert_eqn(eqn) for eqn in eqn_list]
    return eqn_list

def process_eqn(eqn):
    if prog1_include.false_detect(eqn):
        return None  # 返回None代表布尔表达式为假
    else:
        min_sop, _ = prog1_include.minimized_SOP(eqn)
        return str(min_sop)  # 直接返回最小和项积的字符串

# 主程序
input_filename = input("Please select your input file: ")
eqn_list = read_and_process_eqns(input_filename)
print(eqn_list)

dict_list = []  # 初始化列表来存储每个布尔表达式的处理结果
for i, eqn in enumerate(eqn_list):
    minimized_sop = process_eqn(eqn)
    if minimized_sop is None:
        dict_list.append({'error': 'Invalid Boolean expression'})  # 将错误信息添加到列表中
    else:
        dict_list.append({'min_sop': minimized_sop})  # 将成功处理的布尔表达式最小SOP添加到列表中

# 示例：打印所有结果
for i, d in enumerate(dict_list):
    print(f"Boolean Expression {i+1}: {d}")