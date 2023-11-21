import prog1_include
import sympy as sp
import fpga
import itertools
import re


def _generate_sram(expr, variables):
    truth_values = list(itertools.product([False, True], repeat=len(variables)))
    outputs = []
    print(f"expr in function sram: {expr}")
    for vals in truth_values:
        c_value = vals[0]  
        valuation = dict(zip(variables, vals))
        valuation['c'] = c_value  
        result = expr.subs(valuation)
        simplified_result = sp.simplify(result)
        print(result)
        if simplified_result == True:
            outputs.append(1)
        elif simplified_result == False:
            outputs.append(0)
        else:
            raise ValueError(f"Unable to simplify expression to boolean value: {result}")

    return outputs


def read_and_process_eqns(filename):
    eqn_list = prog1_include.read_eqn(filename)
    eqn_list = [prog1_include.convert_eqn(eqn) for eqn in eqn_list]
    return eqn_list

def read_and_process_left(filename):
    eqn_list = prog1_include.read_left(filename)
    eqn_list = [prog1_include.convert_eqn(eqn) for eqn in eqn_list]
    return eqn_list

def process_eqn(eqn):
    if prog1_include.false_detect(eqn):
        return None  # 返回None代表布尔表达式为假
    else:
        min_sop, _ = prog1_include.minimized_SOP(eqn)
        return str(min_sop)  

def read_config(filename):
    config = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = int(value.strip())

    return config

def split_sop(sop):
    product_terms = sop.split('|')
    product_list = [product.strip() for product in product_terms]
    return product_list

def count_letters(s):
    if s is None:
        return 0 
    return len(set(char.lower() for char in s if char.isalpha()))

def count_lines(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return sum(1 for num_line in file)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
    except Exception as e:
        print(f"Error when reading file: {e}")
        return None

def split_prod(expr, group_size=4):
    expr_str = str(expr)
    expr_str = re.sub(r'~(\w+)', r'neg_\1', expr_str)
    modified_expr = sp.sympify(expr_str)
    variables = sorted(modified_expr.free_symbols, key=lambda x: str(x))
    groups = [variables[i:i + group_size] for i in range(0, len(variables), group_size)]
    sub_exprs = [sp.And(*group) for group in groups]
    sub_exprs = [sp.sympify(str(expr).replace('neg_', '~')) for expr in sub_exprs]
    return sub_exprs

def replace_none(main_lut_reg, missing_in, exist_lut_reg):
    processed_main_lut_reg = []
    accepter = []
    donor = []
    
    for item in main_lut_reg:
        number, _ = item.split(':', 1)  # 分割字符串并取第一部分
        accepter.append(int(number))
    
    for item in main_lut_reg:
        val, _    = item.split(':',2)
        donor.append(int(val))
        index, values = item.split(':')
        values = str(eval(values.replace('None', 'None')))
        processed_main_lut_reg.append((index, values))
      
    for accept, donate in zip(accepter, donor):
        fpga.connect_luts(accept, donate)



    map_dict = {item.split(':')[0]: int(item.split(':')[1]) for item in exist_lut_reg}

    for i, (index, values) in enumerate(processed_main_lut_reg):
        for j, value in enumerate(values):
            if value is None:
                try:
                    mapped_value = map_dict[missing_in.pop(0)]
                    processed_main_lut_reg[i][1][j] = mapped_value
                except KeyError as e:
                    return f"KeyError occurred: {e}"
    return processed_main_lut_reg

def get_variable_set(expr):
    all_vars = [sp.symbols(var) for var in 'abcdefgh']
    var_set = set(expr.free_symbols)
    expr_vars = sorted(var_set, key=lambda x: str(x))
    while len(expr_vars) < 4:
        for var in all_vars:
            if var not in expr_vars:
                expr_vars.append(var)
                break
        if len(expr_vars) >= 4:
            break

    return expr_vars[:4] 



def find_number(letter, data_list):
    for item in data_list:
        if item.startswith(letter + ':'):
            return int(item.split(':')[1])
    return None









#main:
sel = input("Please select your format: (b)itstream / (e)quation:\n")
if sel == 'e':
    input_filename = input("Please select your input file: ")
    conf_filename = input("Please select your config file: ")
    config = read_config(conf_filename)
    LUT_NUM = config.get('LUT_NUM', None)
    CON = config.get('CON', None)
    INPUT = config.get('INPUT', None)
    OUTPUT = config.get('OUTPUT', None)
    mem =  LUT_NUM * 16 + LUT_NUM * LUT_NUM + INPUT + OUTPUT
    
    con = 0
    if(CON != 1):
        ValueError("Partial connection not supported")
    else:
        con = LUT_NUM * (LUT_NUM - 1)
        
    line_num = count_lines(input_filename)
    eqn_list = read_and_process_eqns(input_filename)
    left_values = read_and_process_left(input_filename)#找interconnect
    product_list = [None] * line_num#lines of eqn
    al_product_list = [None] * line_num
    line_product_num = [None] * line_num
    line_input_num = 0

    for i, eqn in enumerate(eqn_list):
        minimized_sop = process_eqn(eqn)
        line_input_num = line_input_num + count_letters(minimized_sop)
        
        if minimized_sop is None:
            #print(f"Boolean Expression {i+1} is false")
            product_list[i] = []
            #print(len(product_list[i]))
        else:
            product_list[i] = split_sop(minimized_sop)
            #print(len(product_list[i]))
            #print(product_list[i])
            #len(product_list[i] = 乘积数量)
            #count_letters(product_list[i][j]) = 字母数量


    and_lut_num = 0
    prod_lut_sum = 0
    or_lut_sum = 0
    or_lut_num = 0
    j = 0
    j = int(j)

    fpga = fpga.PartiallyConnectedFPGA(LUT_NUM, INPUT, OUTPUT)

    temp_lut_reg = []
    main_lut_reg = []
    sram_reg = []
    exist_lut_reg = []
    missing_in = []

    line_idx = 0
    line_idx = int(line_idx)
    #product：
    for line in product_list: 
        if not line: #boolean = False Handler
            sram_e = [0] * 16
            fpga.set_lut_sram(j, sram_e)
            main_lut_reg.append(f"{j}:{False}")
            temp_lut_reg.append(j)
                            
        else:    
            #单独product操作开始
            temp_lut_reg = []
            for product in line:
                input_cnt = count_letters(product)
                input_cnt = input_cnt - 4
                sp_product = sp.sympify(product)
                split_prods = split_prod(sp_product)
                #开始切分单独product
                for prod in split_prods:#itr = 1 if num_variable <= 4, itr = num%4 + 1
                    alpha_lut = []
                    prev = j
                    j = j + 1
                    current = j
                    alpha = get_variable_set(prod)  
                    print(alpha)              
                    for sym in alpha:
                        
                        sym_str = str(sym)  # SymPy 转字符串
                        if sym_str in left_values:
                            number = find_number(sym_str, exist_lut_reg)
                            alpha_lut.append(number)
                        else:
                            alpha_lut.append(sym_str)

                    
                    # srams = _generate_sram(sp_product, alpha)
                    # sram_reg.append(srams)
                    # fpga.set_lut_sram(j, srams)
                    print(f"j(lut_idx):{j}")
                    print(len(split_prods))
                    print(prod)
                    if len(split_prods) > 1:
                        await_time = 1
                        srams = _generate_sram(prod, alpha)
                        sram_reg.append(srams)
                        fpga.set_lut_sram(j, srams)
                        name_idx = 0
                        name_idx = int(name_idx)
                        for name in alpha_lut:                    
                            if name == None:
                                miss = str(alpha[name_idx])
                                missing_in.append(miss)
                                print(name_idx)
                            name_idx = name_idx + 1
                        main_lut_reg.append(f"{j}:{str(prev)}{str(current)}{str(prev)}{str(current)}")
                        
                    else:
                        temp_lut_reg.append(j)
                        await_time = 0
                        srams = _generate_sram(sp_product, alpha)
                        sram_reg.append(srams)
                        fpga.set_lut_sram(j, srams)
                        name_idx = 0
                        name_idx = int(name_idx)
                        for name in alpha_lut:                    
                            if name == None:
                                miss = str(alpha[name_idx])
                                missing_in.append(miss)
                                print(name_idx)
                            name_idx = name_idx + 1
                        
                        main_lut_reg.append(f"{j}:{alpha_lut}") #lut idx : connection
                    
                #print(main_lut_reg)
                #print(temp_lut_reg)
                
                #连接分开的多变量product
                
                if await_time == 1: 
                    j = j + 1
                    sram_reg.append([0] * 12 + [1] * 4)
                    fpga.set_lut_sram(j, [0] * 12 + [1] * 4) #both have to be true to get a true
                    fpga.connect_luts(prev, j)
                    fpga.connect_luts(current, j)
                    main_lut_reg.append(f"{j}:{prev}{current}{prev}{current}")
                    temp_lut_reg.append(j)
                    #单独product操作结束
                    #开始实现or函数
                    
            j = j + 1
            main_or = j
            fpga.set_lut_sram(main_or, [0] + [1] * 15) #or gate 
            sram_reg.append([0] + [1] * 15)
            #temp_lut_reg.append(j)
            for prod_lut in temp_lut_reg:
                main_or_remain = 4
                if len(temp_lut_reg) > main_or_remain: #太多product，pop 4 个
                    j = j + 1
                    curr_lut1 = temp_lut_reg.pop(len(temp_lut_reg) - 1) #pop出
                    curr_lut2 = temp_lut_reg.pop(len(temp_lut_reg) - 1) #temp_lut_reg
                    curr_lut3 = temp_lut_reg.pop(len(temp_lut_reg) - 1) #的末位
                    curr_lut4 = temp_lut_reg.pop(len(temp_lut_reg) - 1) 
                    fpga.set_lut_sram(j, [0] + [1] * 15)
                    fpga.connect_luts(curr_lut1, j)
                    fpga.connect_luts(curr_lut2, j)
                    fpga.connect_luts(curr_lut3, j)
                    fpga.connect_luts(curr_lut4, j)
                    
                    fpga.connect_luts(j, main_or) #连回main or lut, 不支持16个以上
                    main_or_remain = main_or_remain - 1
                    if(main_or_remain < 0):
                        ValueError("Too many products in the equation, exceeded 16 maximum")      
                else:
                    print(f"Connect {prod_lut},{main_or}")
                    fpga.connect_luts(prod_lut, main_or)
                    
                    
            if(len(temp_lut_reg) == 2):
                main_lut_reg.append(f"{main_or}:{temp_lut_reg+[0]+[0]}")
            elif(len(temp_lut_reg) == 3):
                main_lut_reg.append(f"{main_or}:{temp_lut_reg+[0]}")
            exist_lut_reg.append(f"{left_values[line_idx]}:{main_or}")
        
        
        print(f"line_idx:{left_values[line_idx]}")
        print(f"exist_lut{exist_lut_reg}")
        line_idx = line_idx + 1
        
    print(f"Missing{missing_in}")

    lut_consumption = (j - 1) / LUT_NUM * 100

    con_active = 0
    for i in range(1, j):
        for k in range(1, j):
            if fpga.crossbar.is_connected(i,k):
                con_active = con_active + 1
    con_consumption = 100 * (con_active) / con       
            
    mem_usage = 100 * (con_active + j * 16 + len(left_values) + input_cnt)/mem        

    print(f"LUT usage rate is {lut_consumption}%")
    print(f"Connection usage rate is {con_consumption}%")
    print(f"Memory usage is {mem_usage}%")
                   
    # print(main_lut_reg)    
    # print(sram_reg)
    final_lut = []
    final_lut = replace_none(main_lut_reg, missing_in, exist_lut_reg)

    for lut in final_lut:
        print(lut)     

    with open('output.elf', 'w') as file:
        for item_A, item_B in zip(final_lut, sram_reg):
            file.write(str(item_A) + '\n')
            file.write(str(item_B) + '\n')
            
                                        

    out = fpga.compute([[1, 1, 1, 1]] * LUT_NUM)
    print(out[:j])   
    print()       

elif sel == 'b':
    lut_idx_bitstr = []
    lut_con_bit = []
    sram_bitstr = []
    
    bitstr_filename = input("Please select your bitstream: \n")
    conf_filename = input("Please select your config file: \n")
    config = read_config(conf_filename)
    LUT_NUM = config.get('LUT_NUM', None)
    CON = config.get('CON', None)
    INPUT = config.get('INPUT', None)
    OUTPUT = config.get('OUTPUT', None)
    mem =  LUT_NUM * 16 + LUT_NUM * LUT_NUM + INPUT + OUTPUT
    fpga = fpga.PartiallyConnectedFPGA(LUT_NUM, INPUT, OUTPUT)
    con = 0
    if(CON != 1):
        ValueError("Partial connection not supported")
    else:
        con = LUT_NUM * (LUT_NUM - 1)
    with open(bitstr_filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('('):
                # 处理形如 ('10', [35, 'a', 'b', 'c']) 的行
                idx, con = eval(line)
                lut_idx_bitstr.append(int(idx))
                lut_con_bit.append(con)
            elif line.startswith('['):
                # 处理形如 [0, 1, 1, 1, ...] 的行
                bitstr = eval(line)
                sram_bitstr.append(bitstr)
    i = 1
    i = int(i)
    j = 0
    j = int(j)
    for input in lut_con_bit:
        fpga.set_lut_sram(i, sram_bitstr[i-1])
        while j < 4:
            if isinstance(lut_con_bit[i-1][j], (int, float)):
                fpga.connect_luts(i, lut_con_bit[i-1][j])
            j = j + 1
        i = i + 1
    
    print(sram_bitstr)
    out = fpga.compute([[1, 1, 1, 1]] * LUT_NUM)
    print(out)   

    # print("lut_idx_bitstr:", lut_idx_bitstr)
    # print("lut_con_bit:", lut_con_bit)
    # print("sram_bitstr:", sram_bitstr)