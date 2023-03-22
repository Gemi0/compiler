#Dominik Gorgosch 261701

import compiler_parser
import sys

def run_compiler(imp_input_path, mr_output_path):
    try:
        compiler_parser.parse_file(imp_input_path, mr_output_path)
    except:
        print('Compiling failed')

if __name__ == "__main__":
    if len(sys.argv) == 3:
        run_compiler(sys.argv[1], sys.argv[2])