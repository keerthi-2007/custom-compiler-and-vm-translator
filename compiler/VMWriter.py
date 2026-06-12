SEG_CONST = "constant"
SEG_ARG = "argument"
SEG_LOCAL = "local"
SEG_STATIC = "static"
SEG_THIS = "this"
SEG_THAT = "that"
SEG_POINTER = "pointer"
SEG_TEMP = "temp"
OP_ADD = "add"
OP_SUB = "sub"
OP_NEG = "neg"
OP_EQ = "eq"
OP_GT = "gt"
OP_LT = "lt"
OP_AND = "and"
OP_OR = "or"
OP_NOT = "not"


class VMWriter:
    def __init__(self, output_path):
        self.output_file = open(output_path, "w")

    def write_push(self, segment, index):
        self.output_file.write(f"push {segment} {index}\n")

    def write_pop(self, segment, index):
        self.output_file.write(f"pop {segment} {index}\n")

    def write_arithmetic(self, operation):
        self.output_file.write(f"{operation}\n")

    def write_label(self, label):
        self.output_file.write(f"label {label}\n")

    def write_goto(self, label):
        self.output_file.write(f"goto {label}\n")

    def write_if_goto(self, label):
        self.output_file.write(f"if-goto {label}\n")

    def write_call(self, subroutine_name, args_count):
        self.output_file.write(f"call {subroutine_name} {args_count}\n")

    def write_function(self, subroutine_name, locals_count):
        self.output_file.write(f"function {subroutine_name} {locals_count}\n")

    def write_return(self):
        self.output_file.write("return\n")

    def close(self):
        self.output_file.close()