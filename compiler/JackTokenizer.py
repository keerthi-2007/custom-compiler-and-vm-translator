import re
import os

TT_KEYWORD = "keyword"
TT_SYMBOL = "symbol"
TT_INT_CONST = "integerConstant"
TT_STRING_CONST = "stringConstant"
TT_IDENTIFIER = "identifier"
TT_NONE = None

KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static",
    "var", "int", "char", "boolean", "void", "true", "false", "null",
    "this", "let", "do", "if", "else", "while", "return"
}

SYMBOLS = set("{}()[].,;+-*/&|<>=~")

JACK_INT_MAX = 32767

XML_ESCAPE = {
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;",
    '"': "&quot;",
}

def _escape_xml(text):
    for ch, esc in XML_ESCAPE.items():
        text = text.replace(ch, esc)
    return text

class JackTokenizer:
    def __init__(self, input_path):
        self.input_path = input_path
        self.tokens = []        
        self.current_index = -1
        self.current_token = None
        self.preserved = False
        self._load_and_tokenize()

    def _load_and_tokenize(self):
        with open(self.input_path, "r") as f:
            source = f.read()

        source = self._strip_comments(source)
        self._tokenize(source)

    def _strip_comments(self, source):
        result = []
        i = 0
        n = len(source)
        in_string = False

        while i < n:
            if in_string:
                result.append(source[i])
                if source[i] == '"':
                    in_string = False
                i += 1
                continue

            if source[i] == '"':
                in_string = True
                result.append(source[i])
                i += 1
                continue

            if source[i] == '/' and i + 1 < n and source[i + 1] == '/':
                while i < n and source[i] != '\n':
                    i += 1
                continue

            if source[i] == '/' and i + 1 < n and source[i + 1] == '*':
                i += 2
                while i < n - 1 and not (source[i] == '*' and source[i + 1] == '/'):
                    i += 1
                i += 2 
                continue

            result.append(source[i])
            i += 1

        return "".join(result)

    def _tokenize(self, source):
        i = 0
        n = len(source)

        while i < n:
            ch = source[i]
            if ch.isspace():
                i += 1
                continue
            if ch in SYMBOLS:
                self.tokens.append((TT_SYMBOL, ch))
                i += 1
                continue
            if ch == '"':
                j = i + 1
                while j < n and source[j] != '"':
                    j += 1
                string_val = source[i + 1:j]
                self.tokens.append((TT_STRING_CONST, string_val))
                i = j + 1
                continue
            if ch.isdigit():
                j = i
                while j < n and source[j].isdigit():
                    j += 1
                val = int(source[i:j])
                if val > JACK_INT_MAX:
                    raise ValueError(f"Integer constant {val} exceeds max {JACK_INT_MAX}")
                self.tokens.append((TT_INT_CONST, val))
                i = j
                continue
            if ch.isalpha() or ch == '_':
                j = i
                while j < n and (source[j].isalnum() or source[j] == '_'):
                    j += 1
                word = source[i:j]
                if word in KEYWORDS:
                    self.tokens.append((TT_KEYWORD, word))
                else:
                    self.tokens.append((TT_IDENTIFIER, word))
                i = j
                continue

            raise ValueError(f"Invalid character: {ch!r}")
        
    def has_more_tokens(self):
        return self.current_index < len(self.tokens) - 1

    def advance(self):
        if self.preserved:
            self.preserved = False
            return
        self.current_index += 1
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]
        else:
            self.current_token = (TT_NONE, None)

    def putback_token(self):
        self.preserved = True

    def get_token_type(self):
        return self.current_token[0] if self.current_token else TT_NONE

    def get_keyword(self):
        assert self.get_token_type() == TT_KEYWORD
        return self.current_token[1]

    def get_symbol(self):
        assert self.get_token_type() == TT_SYMBOL
        return self.current_token[1]

    def get_identifier(self):
        assert self.get_token_type() == TT_IDENTIFIER
        return self.current_token[1]

    def get_int_val(self):
        assert self.get_token_type() == TT_INT_CONST
        return self.current_token[1]

    def get_string_val(self):
        assert self.get_token_type() == TT_STRING_CONST
        return self.current_token[1]

    def throw_exception(self, msg):
        raise RuntimeError(f"{msg} (token index {self.current_index})")

    def write_xml(self, output_path):
        lines = ["<tokens>"]
        for token_type, value in self.tokens:
            escaped = _escape_xml(str(value))
            lines.append(f"  <{token_type}> {escaped} </{token_type}>")
        lines.append("</tokens>")
        with open(output_path, "w") as f:
            f.write("\n".join(lines) + "\n")