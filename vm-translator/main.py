import os
import sys
from parser import Parser
from Code_writer import CodeWriter

def translate_file(vm_path, writer):
    writer.set_file_name(vm_path)
    parser = Parser(vm_path)

    while parser.has_more_commands():
        parser.advance()
        ctype = parser.command_type()
        if ctype == "C_ARITHMETIC":
            writer.write_arithmetic(parser.arg1())

        elif ctype in ("C_PUSH", "C_POP"):
            writer.write_push_pop(ctype, parser.arg1(), parser.arg2())

        elif ctype == "C_LABEL":
            writer.write_label(parser.arg1())

        elif ctype == "C_GOTO":
            writer.write_goto(parser.arg1())

        elif ctype == "C_CALL":
            writer.write_call(parser.arg1(), parser.arg2())

        elif ctype == "C_IF":
            writer.write_if(parser.arg1())

        elif ctype == "C_FUNCTION":
            writer.write_function(parser.arg1(), parser.arg2())

        elif ctype == "C_RETURN":
            writer.write_return()

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <file.vm | directory>")
        sys.exit()
    path = sys.argv[1].rstrip(os.sep)
    if os.path.isfile(path):
        out_path = path.replace(".vm", ".asm")
        writer = CodeWriter(out_path)
        translate_file(path, writer)
        writer.close()
        print(f"Translated --> {out_path}")

    elif os.path.isdir(path):
        dir_name = os.path.basename(path)
        out_path = os.path.join(path, dir_name + ".asm")
        writer = CodeWriter(out_path)
        writer.write_init()

        vm_files = sorted(os.path.join(path, f) for f in os.listdir(path) if f.endswith(".vm"))
        for vm_file in vm_files:
            print(f" Translating {vm_file} ...")
            translate_file(vm_file, writer)

        writer.close()
        print(f"Translated --> {out_path}")

    else:
        print(f"Error: {path} is not a valid .vm file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
