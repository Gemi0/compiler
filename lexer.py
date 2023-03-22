#Dominik Gorgosch 261701

import ply.lex as lex
import sys
import os

tokens = [
    'PROGRAM_IS', 'VAR', 'BEGIN', 'END', 'SEMICOLON', 'COMMA',    # 0 program
    'NUM',                                              # 1 numbers
    'PLUS', 'MINUS', 'TIMES', 'DIV', 'MOD',             # 2 operators
    'EQ', 'NEQ', 'LE', 'GE', 'LEQ', 'GEQ',              # 3 relations
    'ASSIGN',                                           # 4 assign
    'LBR', 'RBR', 'PROCEDURE', 'IS',                    # 5 procedure 
    'IF', 'THEN', 'ELSE', 'ENDIF',                      # 6 if
    'WHILE', 'DO', 'ENDWHILE',                          # 7 while
    'REPEAT', 'UNTIL',                                  # 8 repeat
    'READ', 'WRITE',                                    # 9 read/write
    'ID'                                                # 10 identificators
]

# 0 program
t_ignore_COM = r'\[[^\]\[]*\]'
t_PROGRAM_IS = r'PROGRAM[ ]IS'
t_VAR = r'VAR'
t_BEGIN = r'BEGIN'
t_END = r'END'
t_SEMICOLON = r';'
t_COMMA = r','

# 1 numbers
def t_NUM(t):
    r'[0-9]+'

    t.value = int(t.value)
    return t


# 2 operators
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIV = r'\/'
t_MOD = r'\%'

# 3 relations
t_EQ = r'='
t_NEQ = r'!='
t_LE = r'<'
t_GE = r'>'
t_LEQ = r'<='
t_GEQ = r'>='

# 4 assign
t_ASSIGN = r':='

# 5 arrays
t_PROCEDURE = r'PROCEDURE'
t_LBR = r'\('
t_RBR = r'\)'
t_IS = r'IS'

# 6 if
t_IF = r'IF'
t_THEN = r'THEN'
t_ELSE = r'ELSE'
t_ENDIF = r'ENDIF'

# 7 while
t_WHILE = 'WHILE'
t_DO = 'DO'
t_ENDWHILE = 'ENDWHILE'

# 8 repeat
t_REPEAT = 'REPEAT'
t_UNTIL = 'UNTIL'

# 9 read/write
t_READ = 'READ'
t_WRITE = 'WRITE'

# 10 identificators
t_ID = r'[_a-z]+'

# Define a rule so we can track line NUMs
def t_newline(t):
    r'\r?\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    sys.exit("Illegal character '{}'".format(t.value[0]))
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# data = open("input").read()
# lexer.input(data)
# while True:
#     tok = lexer.token()
#     if not tok:
#        break
#     print(tok)
#     print(lexer.lineno)