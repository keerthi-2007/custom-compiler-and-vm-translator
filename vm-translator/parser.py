class Parser:
    def __init__(self, filepath):
        self.lines = []
        self.current_index = -1
        self.current_command = ""
        with open(filepath, 'r', encoding = "utf-8") as f:
            raw = f.readlines()
        for line in raw:
            clean = line.split('//')[0].strip()
            if clean:
                self.lines.append(clean)

    def has_more_commands(self):
        return self.current_index < len(self.lines) - 1
    
    def advance(self):
        self.current_index += 1
        self.current_command = self.lines[self.current_index]

    def command_type(self):
        first_word = self.current_command.split()[0]
        Arithmetic = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
        if first_word in Arithmetic:
            return "C_ARITHMETIC"
        mapping = {
            "push" : "C_PUSH",
            "pop" : "C_POP",
            "label" : "C_LABEL",
            "goto" : "C_GOTO",
            "if-goto" : "C_IF",
            "function" : "C_FUNCTION",
            "call" : "C_CALL",
            "return" : "C_RETURN",
        }
        return mapping[first_word]
    
    def arg1(self):
        parts = self.current_command.split()
        if self.command_type() == "C_ARITHMETIC":
            return parts[0]
        return parts[1]
    
    def arg2(self):
        return int(self.current_command.split()[2])

        
            