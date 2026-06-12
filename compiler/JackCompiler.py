import sys
import os
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def compile_file(jack_path):
    base = os.path.splitext(jack_path)[0]   
    class_name = os.path.basename(base)      
    dir_name = os.path.dirname(jack_path) or "."

    token_xml_path = os.path.join(dir_name, class_name + "T.xml")
    parse_xml_path = os.path.join(dir_name, class_name + ".xml")
    vm_path        = os.path.join(dir_name, class_name + ".vm")

    print(f"Compiling: {jack_path}")

    tokenizer = JackTokenizer(jack_path)
    tokenizer.write_xml(token_xml_path)
    print(f"  -> {token_xml_path}")

    engine = CompilationEngine(tokenizer, class_name, vm_path, parse_xml_path)
    engine.compile_class()
    print(f"  -> {parse_xml_path}")
    print(f"  -> {vm_path}")


def compile_directory(dir_path):
    jack_files = [
        os.path.join(dir_path, f)
        for f in os.listdir(dir_path)
        if f.endswith(".jack")
    ]
    if not jack_files:
        print(f"No .jack files found in '{dir_path}'")
        return
    for jack_file in sorted(jack_files):
        compile_file(jack_file)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <file.jack | directory>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isdir(target):
        compile_directory(target)
    elif os.path.isfile(target) and target.endswith(".jack"):
        compile_file(target)
    else:
        print(f"Error: '{target}' is not a .jack file or directory.")
        sys.exit(1)


if __name__ == "__main__":
    main()