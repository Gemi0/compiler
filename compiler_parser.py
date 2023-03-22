#Dominik Gorgosch 261701

import sys
import ply.yacc as yacc
from lexer import tokens
import os
import re

jump_counter = 0

# ######## MEMORY MANAGEMENT ########

memory_count = 200
procedures = {}
procedures['main'] = {}
curr_procedure = None
procedure_counter = 10
procedure_inv_counter = 0
procedures_ids = {}


# TMP VARIABLES USE:
# tmp0 never used, because code uses non stop

# tmp1 contains 1
# tmp2 contains jump address
# tmp3-9 used for calculations
# tmp10 - 200 used for procedures
# tmp200 + used for variables

def add_procedure(id, variables, lineno):
    new_id = id[1]
    global curr_procedure
    global memory_count
    global procedures
    global procedure_counter
    curr_procedure = new_id
    if new_id in procedures:
        print('Blad w linii {} : Druga deklaracja {}'.format(lineno, id))
        raise Exception('Blad w linii {} : Druga deklaracja {}'.format(lineno, id))
    vars = {}
    for el in variables:
        if el in vars:
            print('Blad w linii {} : Druga deklaracja {}'.format(lineno, el))
            raise Exception('Blad w linii {} : Druga deklaracja {}'.format(lineno, el))
        vars[el] = (memory_count, True)
        memory_count += 1
    procedures[new_id] = vars
    procedures_ids[new_id] = procedure_counter

def add_variable(id, lineno):
    global curr_procedure
    global memory_count
    global procedures
    vars = procedures[curr_procedure]
    if id in vars:
        print('Blad w linii {} : Druga deklaracja {}'.format(lineno, id))
        raise Exception('Blad w linii {} : Druga deklaracja {}'.format(lineno, id))
    vars[id] = (memory_count, False)
    procedures[curr_procedure] = vars
    memory_count += 1

# ######## HELPERS ########

def mark_var_as_assigned(var, lineno):
    global curr_procedure
    global procedures
    curr = procedures[curr_procedure]
    if var[0] == 'id':
        if var[1] in curr:
            sth = curr[var[1]]
            sth2 = (sth[0], True)
            curr[var[1]] = sth2
            procedures[curr_procedure] = curr
        else:
            print('Blad w linii {} : Nie zdeklarowana zmienna {}'.format(lineno, var[1]))
            raise Exception('Blad w linii {} : Nie zdeklarowana zmienna {}'.format(lineno, var[1]))
    else: 
        print('Blad w linii {} : Nie mozna przypisac wartosci do liczby {}'.format(lineno, id))
        raise Exception('Blad w linii {} : Nie mozna przypisac wartosci do liczby {}'.format(lineno, id))
    
# we wont use this couse we have to take all params to procudere as if they were inicialized 
def mark_vars_as_assigned_to_proc(proc_name, vars):
    name = proc_name[1]
    name = proc_name[1]
    global procedures
    main = procedures["main"]
    curr = procedures[name]
    keys = list(curr.keys())
    counter = 0
    for var in vars:
        key = keys[counter]
        address = curr[key][0]  
        if main[var][1] == True:
            new_var = (address, True)
            curr[key] = new_var
        counter += 1
    procedures[name] = curr

def mark_var_as_assigned_from_proc(proc_name, vars):
    name = proc_name[1]
    global procedures
    global curr_procedure
    main = procedures[curr_procedure]
    curr = procedures[name]
    keys = list(curr.keys())
    counter = 0
    for var in vars:
        address = main[var][0]
        key = keys[counter]
        if curr[key][1] == True:
            new_var = (address, True)
            main[var] = new_var
        counter += 1
    procedures[curr_procedure] = main


def set_vars_to_proc(proc_name, vars, lineno):
    global curr_procedure
    global procedures
    name = proc_name[1]
    if name in procedures:
        
        dest = procedures[proc_name[1]]
        curr = procedures[curr_procedure]
        keys = list(dest.keys())
        counter = 0
        commands = []
        for var in vars:
            address = get_id_adress(("id",var))
            commands.append('LOAD ' + str(address))
            commands.append('STORE ' + str(dest[keys[counter]][0]))
            counter +=1
        return cmd(commands)
    else:
        print('Blad w linii {} : Uzycie nie zadeklarowanej procedury {}'.format(lineno, name))
        raise Exception('Blad w linii {} : Uzycie nie zadeklarowanej procedury {}'.format(lineno, name))
 
    

def from_proc_to_vars(proc_name, vars):
    global curr_procedure
    global procedures
    dest = procedures[proc_name[1]]
    curr = procedures[curr_procedure]
    keys = list(dest.keys())
    counter = 0
    commands = []
    for var in vars:
        address = get_id_adress(("id",var))
        commands.append('LOAD ' + str(dest[keys[counter]][0]) )
        commands.append('STORE ' + str(address))
        counter +=1
    return cmd(commands)

def get_proc_id(proc_name):
    global procedures_ids
    return procedures_ids[proc_name[1]]

def load_value_to_adres(value, adres, lineno):
    global procedures
    global curr_procedure
    if value[0] == 'num':
        return put_const_to_adres(value[1], adres)
    elif value[0] == 'id':
        curr = procedures[curr_procedure]
        if value[1] in curr:

            if curr[value[1]][1] == True:
                if adres == 0:
                    return cmd(['LOAD ' + str(curr[value[1]][0])])
                else:
                    return cmd([
                        'LOAD ' + str(curr[value[1]][0]),
                        'STORE ' + str(adres)
                    ])
            else:
                print('Mozliwy blad w linii {} : Uzycie nie zainicjowanej zmiennej {}'.format(lineno, value[1]))
                #raise Exception('Blad w linii {} : Uzycie nie zainicjowanej zmiennej {}'.format(lineno, value[1]))
                if adres == 0:
                    return cmd(['LOAD ' + str(curr[value[1]][0])])
                else:
                    return cmd([
                        'LOAD ' + str(curr[value[1]][0]),
                        'STORE ' + str(adres)
                    ])
                
        else:
            print('Blad w linii {} : Nie zadeklarowana zmienna {}'.format(lineno, value[1]))
            raise Exception('Blad w linii {} : Nie zadeklarowana zmienna {}'.format(lineno, value[1]))
    else:
        print("Cannot load value to adres, type not recognized. Line {}".format(lineno))
        raise Exception("Cannot load value to adres, type not recognized. Line {}".format(lineno))

def put_const_to_adres(num, adres):
    commands = []
    commands.append('SET ' + str(num))
    if adres != 0:
        commands.append('STORE {}'.format(adres))
    return cmd(commands, 'cnst')

def get_id_adress(id):
    global curr_procedure
    curr = procedures[curr_procedure]
    if id[0] == 'id':
        return curr[id[1]][0]
    

def gen_jump_labels(n):
    global jump_counter
    jump_lines = []
    jump_instructions = []

    for _ in range(n):
        jump_lines.append('@JL{}'.format(jump_counter))
        jump_instructions.append('@JI{}'.format(jump_counter))
        jump_counter += 1

    return jump_lines, jump_instructions

def cmd(cmd_list, opname=None):
    unpacked_list = []

    for cmd_el in cmd_list:
        if isinstance(cmd_el, list):
            for list_el in cmd_el:
                unpacked_list.append(list_el)
        else:
            unpacked_list.append(cmd_el)

    prefixed_list = []

    if opname is not None:
        opname = '[' + opname + '] '
    else:
        opname = ''

    for idx, un_list_el in enumerate(unpacked_list):
        if idx == 0:
            prefix_str = opname
        else:
            prefix_str = len(opname) * ' '

        if isinstance(un_list_el, str):
            prefixed_list.append({'prefix': prefix_str, 'instr': un_list_el})
        elif isinstance(un_list_el, dict):
            prefixed_list.append({'prefix': prefix_str + un_list_el['prefix'], 'instr': un_list_el['instr']})

    return prefixed_list

def build_cmd_to_code_pseudocode(prefixed_list):
    lines = [(el['prefix'] + el['instr']) for el in prefixed_list]

    return '\n'.join(lines)

def build_cmd_to_code_machinecode(prefixed_list):
    instr_list = [el['instr'].strip() for el in prefixed_list]
    JL_to_instr_count = {}
    instr_count = 0
    instr_list_no_JL = []
    instr_list_no_JL_no_JI = []

    for instr in instr_list:
        if instr[:3] == '@JL':
            JL_to_instr_count[instr[3:]] = instr_count
        else:
            instr_count += 1
            instr_list_no_JL.append(instr)

    for instr in instr_list_no_JL:
        if instr.split(' ')[-1][:3] == '@JI':
            jump_JI_num = instr.split(' ')[-1][3:]
            jump_type = instr.split(' ')[0]
            changed_command = jump_type + ' ' + str(JL_to_instr_count[jump_JI_num])
            instr_list_no_JL_no_JI.append(changed_command)
        else:
            instr_list_no_JL_no_JI.append(instr)

    return '\n'.join(instr_list_no_JL_no_JI)

# ######## PARSER ########

JLP, JIP = gen_jump_labels(5000) # jumps for defining procedure

JLE, JIE = gen_jump_labels(5000) # jumps for procedure call

def p_program_all(p):
    """program_all : procedures main"""
    p[0] = cmd([
            'JUMP ' + JIP[0],
            p[1],
            JLP[0],
            p[2],
        ], 'all')

def p_procedures_with_declaration(p):
    """procedures : procedures PROCEDURE proc_head IS VAR declarations BEGIN commands END"""
    global procedure_counter
    p[0] = cmd([
            p[1],
            JLP[procedure_counter],
            p[6],
            p[8],
            'JUMPI ' + str(get_proc_id(p[3])),
        ], 'proc')
    procedure_counter += 1

def p_procedures(p):
    """procedures : procedures PROCEDURE proc_head IS BEGIN commands END"""
    global procedure_counter
    p[0] = cmd([
            p[1],
            JLP[procedure_counter],
            p[6],
            'JUMPI ' + str(get_proc_id(p[3])),
        ], 'proc')
    procedure_counter += 1

def p_program_empty(p):
    """procedures : """
    p[0] = None

def p_main_with_declarations(p):
    """main : init VAR declarations BEGIN commands END"""
    p[0] = cmd([
            'SET 1',
            'STORE 1',
            p[3],
            p[5],
            'HALT',
        ], 'prog')

def p_main_without_declarations(p):
    """main : init BEGIN commands END"""
    p[0] = cmd([
            'SET 1',
            'STORE 1',
            p[3],
            'HALT',
        ], 'prog')

def p_init_main(p):
    """init : PROGRAM_IS"""
    global curr_procedure
    curr_procedure = 'main'
    p[0] = None

def p_commands_many(p):
    """commands : commands command"""
    p[0] = cmd([
        p[1],
        p[2],
    ])

def p_commands_single(p):
    """commands : command"""
    p[0] = cmd([
        p[1]
    ])

def p_command_assign(p):
    """command : identifier ASSIGN expression SEMICOLON"""
    mark_var_as_assigned(p[1], p.lineno(1))
    p[0] = cmd([
        p[3],
        'STORE ' + str(get_id_adress(p[1])),
    ], 'assgn')

def p_command_if_then_else(p):
    """command : IF condition THEN commands ELSE commands ENDIF"""
    # condition is evaluated into tmp0 positive value is True negative or zero False
    JL, JI = gen_jump_labels(2)

    p[0] = cmd([
        p[2],
        'JZERO ' + JI[0],
        p[4],
        'JUMP ' + JI[1],
        JL[0],
        p[6],
        JL[1],
    ], 'ifel')

def p_command_if_then(p):
    """command : IF condition THEN commands ENDIF"""
    # condition is evaluated into tmp0 positive value is True negative or zero False
    JL, JI = gen_jump_labels(1)

    p[0] = cmd([
        p[2],
        'JZERO ' + JI[0],
        p[4],
        JL[0],
    ], 'if')

def p_command_while_do(p):
    """command : WHILE condition DO commands ENDWHILE"""
    # condition is evaluated into tmp0 positive value is True negative or zero False
    JL, JI = gen_jump_labels(3)

    p[0] = cmd([
        JL[1],
        p[2],
        'JPOS ' + JI[2],
        'JUMP ' + JI[0],
        JL[2],
        p[4],
        'JUMP ' + JI[1],
        JL[0],
    ], 'whldo')

def p_command_repeat_until(p):
    """command : REPEAT commands UNTIL condition SEMICOLON"""
    # condition is evaluated into tmp0 positive value is True negative or zero False
    JL, JI = gen_jump_labels(2)

    p[0] = cmd([
        JL[0],
        p[2],
        p[4],
        'JZERO ' + JI[0],
    ], 'dowhl')

def p_command_proc_head(p):
    """command : proc_head_command SEMICOLON"""
    p[0] = p[1]

def p_command_read(p):
    """command : READ identifier SEMICOLON"""
    mark_var_as_assigned(p[2], p.lineno(2))
    p[0] = cmd([
        'GET 0',
        'STORE ' + str(get_id_adress(p[2])),
    ], 'assgn')

def p_command_write(p):
    """command : WRITE value SEMICOLON"""
    p[0] = cmd([
        load_value_to_adres(p[2], 0, p.lineno(1)),
        'PUT 0'
    ], 'wrt')

def p_proc_head_command(p):
    """proc_head_command : identifier LBR proc_declarations RBR """
    global procedure_inv_counter
    p[0] = cmd([
        set_vars_to_proc(p[1], p[3], p.lineno(1)),
        'SET ' + JIE[procedure_inv_counter],
        'STORE ' + str(get_proc_id(p[1])),
        'JUMP ' + JIP[get_proc_id(p[1])],
        JLE[procedure_inv_counter],
        from_proc_to_vars(p[1], p[3]),
    ], 'proc_jump')
    procedure_inv_counter += 1 
    mark_var_as_assigned_from_proc(p[1], p[3])

def p_proc_head(p):
    """proc_head : identifier LBR proc_declarations RBR """
    p[0] = p[1]
    add_procedure(p[1], p[3], p.lineno(3))

def p_proc_declarations_commasep_single(p):
    """proc_declarations : proc_declarations COMMA ID"""
    p[1].append(p[3])
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))

def p_proc_declarations_single(p):
    """proc_declarations : ID"""
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))

def p_declarations_commasep_single(p):
    """declarations : declarations COMMA ID"""
    p[0] = cmd([
        p[1],
    ])
    add_variable(p[3], p.lineno(3))

def p_declarations_single(p):
    """declarations : ID"""
    p[0] = None
    add_variable(p[1], p.lineno(1))

def p_expression_val(p):
    """expression : value"""
    p[0] = cmd([
        load_value_to_adres(p[1], 0, p.lineno(1)),
    ])

def p_expression_val_plus(p):
    """expression : value PLUS value"""
    p[0] = cmd([
            load_value_to_adres(p[1], 3, p.lineno(1)),
            load_value_to_adres(p[3], 0, p.lineno(3)),
            'ADD 3',
        ], 'plus')

def p_expression_val_minus(p):
    """expression : value MINUS value"""
    p[0] = cmd([
            load_value_to_adres(p[3], 3, p.lineno(1)),
            load_value_to_adres(p[1], 0, p.lineno(3)),
            'SUB 3',
        ], 'minus')

def p_expression_val_times(p):
    """expression : value TIMES value"""

    # X * Y
    # tmp3 contains X
    # tmp4 contains Y
    # tmp5 contains pow
    # tmp6 contains acc
    # tmp7 contains sum
    # tmp8 contains Z

    if (p[1][0] == 'num' and p[1][1] == 2):
        p[0] = cmd([
        load_value_to_adres(p[3], 0, p.lineno(3)),
        'ADD 0',
        ])
    elif (p[3][0] == 'num' and p[3][1] == 2):
        p[0] = cmd([
        load_value_to_adres(p[1], 0, p.lineno(1)),
        'ADD 0',
        ])
    else: 
        JL, JI = gen_jump_labels(5)
        p[0] = cmd([
        load_value_to_adres(p[1], 3, p.lineno(1)),
        load_value_to_adres(p[3], 0, p.lineno(3)),
        'SUB 0',
        'JZERO ' + JI[3],
        load_value_to_adres(p[3], 4, p.lineno(3)),
        'JUMP ' + JI[4],
        JL[3],
        load_value_to_adres(p[1], 4, p.lineno(1)),
        load_value_to_adres(p[3], 3, p.lineno(3)),
        JL[4],
        'SET 1',   # init pow
        'STORE 5',
        'LOAD 3', # init acc
        'STORE 6',
        'LOAD 4', # init Z
        'STORE 8',
        'SET 0', # init sum
        'STORE 7',

        JL[0], # end of inicialization
        'LOAD 8',
        'JZERO ' + JI[1], # if z == 0: end

        'LOAD 5', # pow += pow
        'ADD 5',
        'STORE 5',
        'SUB 8', # 0 if z < pow, else > 0
        'JPOS ' + JI[2], # pow is too big

        'LOAD 6', # acc += acc
        'ADD 6',
        'STORE 6',
        'JUMP ' + JI[0],

        JL[2], # pow too big half it and acc to sum
        'LOAD 5',
        'HALF',
        'STORE 5', # half curr pow
        'LOAD 8',
        'SUB 5',
        'STORE 8',
        'LOAD 7',
        'ADD 6',
        'STORE 7', # sum += pow
        'SET 1',
        'STORE 5',
        'LOAD 3',
        'STORE 6',
        'JUMP ' + JI[0],

        JL[1],
        'LOAD 7',
        ], 'tms')

def p_expression_val_div(p):
    """expression : value DIV value"""
    # X / Y
    # tmp3 contains X
    # tmp4 contains Y
    # tmp5 contains mod
    # tmp6 contains l
    # tmp7 contains acc
    # tmp8 contains result
    if (p[3][0] == 'num' and p[3][1] == 2):
        p[0] = cmd([
        load_value_to_adres(p[1], 0, p.lineno(3)),
        'HALF',
        ])
    elif (p[3][0] == 'num' and p[3][1] == 4):
        p[0] = cmd([
        load_value_to_adres(p[1], 0, p.lineno(3)),
        'HALF',
        'HALF',
        ])
    else: 
        JL, JI = gen_jump_labels(4)
        p[0] = cmd([
        load_value_to_adres(p[1], 3, p.lineno(1)),
        load_value_to_adres(p[3], 4, p.lineno(3)),
        load_value_to_adres(p[1], 5, p.lineno(1)),
        load_value_to_adres(p[3], 7, p.lineno(1)),
        'LOAD 4',
        'JZERO ' + JI[0],
        'SET 1', 
        'STORE 6', # l = 1
        'SET 0',
        'STORE 8', # res = 0

        JL[1],
        'LOAD 4',
        'SUB 5',
        'JPOS ' + JI[2], # if mod < Y end
        
        'LOAD 7', # acc += acc
        'ADD 7',
        'STORE 7',
        'SUB 5', # if acc > mod then half and add to sum
        'JPOS ' + JI[3],
        'LOAD 6', # l = l * 2
        'ADD 6',
        'STORE 6', 
        'JUMP ' + JI[1],


        JL[3], # acc too big
        'LOAD 7',
        'HALF',
        'STORE 7', #half acc
        'LOAD 5',
        'SUB 7',
        'STORE 5', # mod = mod - acc
        'LOAD 8',
        'ADD 6',
        'STORE 8', # res = res + l
        'SET 1',
        'STORE 6', # l = 1
        'LOAD 4',
        'STORE 7',
        'JUMP ' + JI[1],

        JL[2], #end
        'LOAD 8',
        JL[0],
        ], 'div')
    

def p_expression_val_mod(p):
    """expression : value MOD value"""
    # X % Y
    # tmp103 contains X
    # tmp104 contains Y
    # tmp105 contains mod
    # tmp106 contains l
    # tmp107 contains acc
    # tmp108 contains result

    JL, JI = gen_jump_labels(4)
    p[0] = cmd([
        load_value_to_adres(p[1], 3, p.lineno(1)),
        load_value_to_adres(p[3], 4, p.lineno(3)),
        load_value_to_adres(p[1], 5, p.lineno(1)),
        load_value_to_adres(p[3], 7, p.lineno(1)),
        'LOAD 4',
        'JZERO ' + JI[2],
        'SET 1', 
        'STORE 6', # l = 1

        JL[1],
        'LOAD 4',
        'SUB 5',
        'JPOS ' + JI[2], # if mod < Y end
        
        'LOAD 7', # acc += acc
        'ADD 7',
        'STORE 7',
        'SUB 5', # if acc > mod then half and add to sum
        'JPOS ' + JI[3],
        'LOAD 6', # l = l * 2
        'ADD 6',
        'STORE 6', 
        'JUMP ' + JI[1],


        JL[3], # acc too big
        'LOAD 7',
        'HALF',
        'STORE 7', #half acc
        'LOAD 5',
        'SUB 7',
        'STORE 5', # mod = mod - acc
        'SET 1',
        'STORE 6', # l = 1
        'LOAD 4',
        'STORE 7',
        'JUMP ' + JI[1],

        JL[2], #end
        'LOAD 5',
        ], 'mod')

def p_condition_val_eq(p):
    """condition : value EQ value"""
    # after evaluation p0 contains 0 or 1 1 if true 0 if false
    JL, JI = gen_jump_labels(2)

    p[0] = cmd([
            load_value_to_adres(p[1], 3, p.lineno(1)),
            load_value_to_adres(p[3], 0, p.lineno(3)),
            'SUB 3',
            'JPOS ' + JI[0],
            load_value_to_adres(p[3], 3, p.lineno(1)),
            load_value_to_adres(p[1], 0, p.lineno(3)),
            'SUB 3',
            'JPOS ' +  JI[0],
            'SET 1',
            'JUMP ' + JI[1],
            JL[0], 
            'SET 0',
            JL[1],
        ], 'veqv')

def p_condition_val_neq(p):
    """condition : value NEQ value"""
    # after evaluation p0 contains 0 or 1 1 if true 0 if false
    JL, JI = gen_jump_labels(2)

    p[0] = cmd([
            load_value_to_adres(p[1], 3, p.lineno(1)),
            load_value_to_adres(p[3], 0, p.lineno(3)),
            'SUB 3',
            'JPOS ' + JI[1],
            load_value_to_adres(p[3], 3, p.lineno(1)),
            load_value_to_adres(p[1], 0, p.lineno(3)),
            'SUB 3',
            'JPOS ' +  JI[1],
            'SET 0',
            'JUMP ' + JI[0],
            JL[1],
            'SET 1',
            JL[0],
        ], 'vneqv')

def p_condition_val_le(p):
    """condition : value LE value"""
    p[0] = cmd([
        load_value_to_adres(p[1], 3, p.lineno(1)),
        load_value_to_adres(p[3], 0, p.lineno(3)),
        'SUB 3',
    ], 'vlev')

def p_condition_val_ge(p):
    """condition : value GE value"""
    
    p[0] = cmd([
            load_value_to_adres(p[3], 3, p.lineno(1)),
            load_value_to_adres(p[1], 0, p.lineno(3)),
            'SUB 3',
        ], 'vgev')

def p_condition_val_leq(p):
    """condition : value LEQ value"""

    JL, JI = gen_jump_labels(2)

    p[0] = cmd([
            load_value_to_adres(p[3], 3, p.lineno(1)),
            load_value_to_adres(p[1], 0, p.lineno(3)),
            'SUB 3',
            'JZERO ' + JI[0],
            'SET 0',
            'JUMP ' + JI[1],
            JL[0],
            'SET 1',
            JL[1],
    ], 'vleqv')

def p_condition_val_geq(p):
    """condition : value GEQ value"""

    JL, JI = gen_jump_labels(2)

    p[0] = cmd([
            load_value_to_adres(p[1], 3, p.lineno(1)),
            load_value_to_adres(p[3], 0, p.lineno(3)),
            'SUB 3',
            'JZERO ' + JI[0],
            'SET 0',
            'JUMP ' + JI[1],
            JL[0],
            'SET 1',
            JL[1],
        ], 'vgeqv')

def p_value_num(p):
    """value : NUM"""
    p[0] = ("num", p[1])
    p.set_lineno(0, p.lineno(1))

def p_value_id(p):
    """value : identifier"""
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))

def p_identifier_id(p):
    """identifier : ID"""
    p[0] = ("id", p[1])
    p.set_lineno(0, p.lineno(1))

def p_error(p):
    sys.exit("error sys.exit")

parser = yacc.yacc()

def parse_file(imp_input_path, mr_output_path):
    with open(imp_input_path, 'r') as f_in:
        code_dev = f_in.read()
        list_code_repr = parser.parse(code_dev, debug=0)
        
    with open(mr_output_path, 'w') as f_out:
        code_dev_machine = build_cmd_to_code_machinecode(list_code_repr)
        f_out.write(code_dev_machine)
