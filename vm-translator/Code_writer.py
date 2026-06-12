import os
class CodeWriter:
    def __init__(self, output_path):
        self.file = open(output_path, 'w')
        self.filename = ""
        self._label_counter = 0
    
    def set_file_name(self, filepath):
        self.filename = os.path.splitext(os.path.basename(filepath))[0]

    def write_init(self):
        self._emit("//bootstrap")
        self._emit("@256")
        self._emit("D=A")
        self._emit("@SP")
        self._emit("M=D")
        self.write_call("Sys.init", 0)

    def write_arithmetic(self, command):
        self._emit(f"//{command}")
        if command == "add":
            self._binary("D+M")
        elif command == "sub":
            self._binary("M-D")
        elif command == "and":
            self._binary("D&M")
        elif command == "or":
            self._binary("D|M")
        elif command == "neg":
            self._unary("-M")
        elif command == "not":
            self._unary("!M")
        elif command in ("eq", "gt", "lt"):
            self._compare(command)
    
    def write_push_pop(self, command, segment, index):
        cmd_str = "push" if command == "C_PUSH" else "pop"
        self._emit(f"// {cmd_str} {segment} {index}")
        if command == "C_PUSH":
            self._push(segment, index)
        else:
            self._pop(segment, index)

    def write_label(self, label):
        self._emit(f"//label {label}")
        self._emit(f"({self._scoped(label)})")

    def write_goto(self, label):
        self._emit(f"//goto {label}")
        self._emit(f"@{self._scoped(label)}")
        self._emit("0;JMP")

    def write_if(self, label):
        self._emit(f"// if-goto {label}")
        self._pop_d()
        self._emit(f"@{self._scoped(label)}")
        self._emit("D;JNE")

    def write_function(self, function_name, n_vars):
        self._emit(f"// function {function_name} {n_vars}")
        self._emit(f"({function_name})")
        for _ in range(n_vars):
            self._emit("@SP")
            self._emit("A=M")
            self._emit("M=0")
            self._emit("@SP")
            self._emit("M=M+1")

    def write_call(self, function_name: str, n_args: int):
        return_label = f"{function_name}$ret.{self._label_counter}"
        self._label_counter += 1
        self._emit(f"// call {function_name} {n_args}")
        self._emit(f"@{return_label}")
        self._emit("D=A")
        self._push_d()
        for seg in ("LCL", "ARG", "THIS", "THAT"):
            self._emit(f"@{seg}")
            self._emit("D=M")
            self._push_d()

        self._emit("@SP")
        self._emit("D=M")
        self._emit(f"@{n_args + 5}")
        self._emit("D=D-A")
        self._emit("@ARG")
        self._emit("M=D")

        self._emit("@SP")
        self._emit("D=M")
        self._emit("@LCL")
        self._emit("M=D")
 
        self._emit(f"@{function_name}")
        self._emit("0;JMP")
 
        self._emit(f"({return_label})")

    def write_return(self):
        self._emit("// return")
        self._emit("@LCL")
        self._emit("D=M")
        self._emit("@R14")
        self._emit("M=D")
    
        self._emit("@5")
        self._emit("A=D-A")
        self._emit("D=M")
        self._emit("@R15")
        self._emit("M=D")

        self._pop_d()
        self._emit("@ARG")
        self._emit("A=M")
        self._emit("M=D")

        self._emit("@ARG")
        self._emit("D=M+1")
        self._emit("@SP")
        self._emit("M=D")

        for i, seg in enumerate(("THAT", "THIS", "ARG", "LCL"), start = 1):
            self._emit("@R14")
            self._emit("D=M")
            self._emit(f"@{i}")
            self._emit("A=D-A")
            self._emit("D=M")
            self._emit(f"@{seg}")
            self._emit("M=D")

        self._emit("@R15")
        self._emit("A=M")
        self._emit("0;JMP")

    def close(self):
        self.file.close()

    def _emit(self, line):
        self.file.write(line + "\n")

    def _scoped(self, label):
        return label
    
    def _push_d(self):
        self._emit("@SP")
        self._emit("A=M")
        self._emit("M=D")
        self._emit("@SP")
        self._emit("M=M+1")

    def _pop_d(self):
        self._emit("@SP")
        self._emit("M=M-1")
        self._emit("A=M")
        self._emit("D=M")

    def _unary(self, op):
        self._emit("@SP")
        self._emit("A=M-1")
        self._emit(f"M={op}")

    def _binary(self, op):
        self._pop_d()
        self._emit("@SP")
        self._emit("A=M-1")
        self._emit(f"M={op}")

    def _compare(self, command):
        true_label = f"TRUE_{self._label_counter}"
        end_label = f"END_{self._label_counter}"
        self._label_counter += 1

        jump = {"eq":"JEQ", "gt":"JGT", "lt":"JLT"}[command]
        
        self._pop_d()
        self._emit("@SP")
        self._emit("A=M-1")
        self._emit("D=M-D")
        self._emit(f"@{true_label}")
        self._emit(f"D;{jump}")

        self._emit("@SP")
        self._emit("A=M-1")
        self._emit("M=0")
        self._emit(f"@{end_label}")
        self._emit("0;JMP")

        self._emit(f"({true_label})")
        self._emit("@SP")
        self._emit("A=M-1")
        self._emit("M=-1")
        self._emit(f"({end_label})")

    def _push(self, segment, index):
        if segment == "constant":
            self._emit(f"@{index}")
            self._emit("D=A")
            #self._push_d()
        elif segment in ("local", "argument", "this", "that"):
            base = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT"}[segment]
            self._emit(f"@{base}")
            self._emit("D=M")
            self._emit(f"@{index}")
            self._emit("A=D+A")
            self._emit("D=M")
            #self._push_d()

        elif segment == "temp":
            self._emit(f"@{5 + index}")
            self._emit("D=M")
            #self._push_d()

        elif segment == "static":
            self._emit(f"@{self.filename}.{index}")
            self._emit("D=M")
            #self._push_d()
        elif segment == "pointer":
            reg = "THIS" if index == 0 else "THAT"
            self._emit(f"@{reg}")
            self._emit("D=M")

        self._push_d()

    def _pop(self, segment, index):
        if segment in {"local", "argument", "this", "that"}:
            base = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT"}[segment]
            self._emit(f"@{base}")
            self._emit("D=M")
            self._emit(f"@{index}")
            self._emit("D=D+A")
            self._emit("@R13")
            self._emit("M=D")
            self._pop_d()
            self._emit("@R13")
            self._emit("A=M")
            self._emit("M=D")

        elif segment == "temp":
            self._pop_d()
            self._emit(f"@{5+index}")
            self._emit("M=D")

        elif segment == "pointer":
            reg = "THIS" if index == 0 else "THAT"
            self._pop_d()
            self._emit(f"@{reg}")
            self._emit("M=D")

        elif segment == "static":
            self._pop_d()
            self._emit(f"@{self.filename}.{index}")
            self._emit("M=D")















