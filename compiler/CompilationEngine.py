from JackTokenizer import (
    TT_KEYWORD, TT_SYMBOL, TT_INT_CONST, TT_STRING_CONST, TT_IDENTIFIER, TT_NONE
)
from SymbolTable import (
    SymbolTable,
    KIND_STATIC, KIND_FIELD, KIND_ARG, KIND_LOCAL, KIND_NONE
)
from VMWriter import (
    VMWriter,
    SEG_CONST, SEG_ARG, SEG_LOCAL, SEG_STATIC,
    SEG_THIS, SEG_THAT, SEG_POINTER, SEG_TEMP,
    OP_ADD, OP_SUB, OP_NEG, OP_EQ, OP_GT, OP_LT, OP_AND, OP_OR, OP_NOT
)

VALID_OPS = set("+-*/&|<>=")
def _segment_of(kind):
    return {
        KIND_ARG: SEG_ARG,
        KIND_FIELD: SEG_THIS,
        KIND_LOCAL: SEG_LOCAL,
        KIND_STATIC: SEG_STATIC,
    }[kind]


class CompilationEngine:
    def __init__(self, tokenizer, class_name, vm_output_path, xml_output_path):
        self.tokenizer = tokenizer
        self.class_name = class_name         
        self.vm_writer = VMWriter(vm_output_path)
        self.symbol_table = SymbolTable()
        self.label_counter = 0
        self.xml_lines = []                   
        self.xml_output_path = xml_output_path

    def _gen_label(self):
        label = f"LABEL{self.label_counter}"
        self.label_counter += 1
        return label

    def _full_name(self, subroutine_name):
        return f"{self.class_name}.{subroutine_name}"

    def _xml(self, tag, value):
        from JackTokenizer import _escape_xml
        self.xml_lines.append(f"<{tag}> {_escape_xml(str(value))} </{tag}>")

    def _xml_open(self, tag):
        self.xml_lines.append(f"<{tag}>")

    def _xml_close(self, tag):
        self.xml_lines.append(f"</{tag}>")

    def _write_xml_file(self):
        with open(self.xml_output_path, "w") as f:
            f.write("\n".join(self.xml_lines) + "\n")

    def _advance(self):
        self.tokenizer.advance()

    def _putback(self):
        self.tokenizer.putback_token()

    def _expect_keyword(self, keyword):
        self._advance()
        if (self.tokenizer.get_token_type() == TT_KEYWORD and
                self.tokenizer.get_keyword() == keyword):
            self._xml(TT_KEYWORD, keyword)
        else:
            self.tokenizer.throw_exception(f"Expected keyword '{keyword}'")

    def _expect_symbol(self, symbol):
        self._advance()
        if (self.tokenizer.get_token_type() == TT_SYMBOL and
                self.tokenizer.get_symbol() == symbol):
            self._xml(TT_SYMBOL, symbol)
        else:
            self.tokenizer.throw_exception(f"Expected symbol '{symbol}'")

    def _expect_identifier(self, id_type="none", var_type="", var_kind=KIND_NONE):
        """
        id_type: "declaration" | "usage" | "none"
        """
        self._advance()
        if self.tokenizer.get_token_type() != TT_IDENTIFIER:
            self.tokenizer.throw_exception("Expected identifier")

        name = self.tokenizer.get_identifier()

        if id_type == "declaration":
            if self.symbol_table.kind_of(name) != KIND_NONE:
                self.tokenizer.throw_exception(f"Identifier '{name}' already declared")
            self.symbol_table.define(name, var_type, var_kind)
        elif id_type == "usage":
            if self.symbol_table.kind_of(name) == KIND_NONE:
                # Allow class names / subroutine names that aren't in symbol table
                pass

        self._xml(TT_IDENTIFIER, name)
        return name

    def _is_next_op(self):
        self._advance()
        result = (self.tokenizer.get_token_type() == TT_SYMBOL and
                  self.tokenizer.get_symbol() in VALID_OPS)
        self._putback()
        return result

    def _is_next_term(self):
        self._advance()
        tt = self.tokenizer.get_token_type()
        result = (
            tt == TT_INT_CONST or
            tt == TT_STRING_CONST or
            (tt == TT_KEYWORD and self.tokenizer.get_keyword() in ("true", "false", "null", "this")) or
            tt == TT_IDENTIFIER or
            (tt == TT_SYMBOL and self.tokenizer.get_symbol() == '(') or
            (tt == TT_SYMBOL and self.tokenizer.get_symbol() in ('-', '~'))
        )
        self._putback()
        return result


    def _write_op(self, op, unary=False):
        mapping = {
            '+': OP_ADD,
            '-': OP_NEG if unary else OP_SUB,
            '*': None,   
            '/': None,   
            '&': OP_AND,
            '|': OP_OR,
            '<': OP_LT,
            '>': OP_GT,
            '=': OP_EQ,
        }
        if op == '*':
            self.vm_writer.write_call("Math.multiply", 2)
        elif op == '/':
            self.vm_writer.write_call("Math.divide", 2)
        else:
            self.vm_writer.write_arithmetic(mapping[op])

    def compile_class(self):
        """class: 'class' className '{' classVarDec* subroutineDec* '}'"""
        self.symbol_table.clear()
        self._xml_open("class")

        self._expect_keyword("class")
        name = self._expect_identifier(id_type="none")
        if name != self.class_name:
            self.tokenizer.throw_exception(
                f"Class name '{name}' must match filename '{self.class_name}'"
            )
        self._expect_symbol('{')

        while self._compile_class_var_dec():
            pass
        while self._compile_subroutine():
            pass

        self._expect_symbol('}')
        self._xml_close("class")

        self.vm_writer.close()
        self._write_xml_file()

    def _compile_class_var_dec(self):
        """('static'|'field') type varName (','varName)* ';'"""
        self._advance()
        if self.tokenizer.get_token_type() != TT_KEYWORD:
            self._putback()
            return False
        kw = self.tokenizer.get_keyword()
        if kw not in ("static", "field"):
            self._putback()
            return False

        self._xml_open("classVarDec")
        self._xml(TT_KEYWORD, kw)
        var_kind = KIND_STATIC if kw == "static" else KIND_FIELD

        var_type = self._compile_type()
        self._expect_identifier("declaration", var_type, var_kind)

        while True:
            self._advance()
            if self.tokenizer.get_token_type() == TT_SYMBOL and self.tokenizer.get_symbol() == ',':
                self._xml(TT_SYMBOL, ',')
                self._expect_identifier("declaration", var_type, var_kind)
            else:
                self._putback()
                break

        self._expect_symbol(';')
        self._xml_close("classVarDec")
        return True

    def _compile_type(self):
        """'int'|'char'|'boolean'|className"""
        self._advance()
        tt = self.tokenizer.get_token_type()
        if tt == TT_KEYWORD and self.tokenizer.get_keyword() in ("int", "char", "boolean"):
            t = self.tokenizer.get_keyword()
            self._xml(TT_KEYWORD, t)
            return t
        elif tt == TT_IDENTIFIER:
            t = self.tokenizer.get_identifier()
            self._xml(TT_IDENTIFIER, t)
            return t
        else:
            self.tokenizer.throw_exception("Expected type")

    def _compile_subroutine(self):
        """('constructor'|'function'|'method') ('void'|type) subroutineName '(' paramList ')' subroutineBody"""
        self.symbol_table.start_subroutine()
        self._advance()

        if self.tokenizer.get_token_type() != TT_KEYWORD:
            self._putback()
            return False
        kw = self.tokenizer.get_keyword()
        if kw not in ("constructor", "function", "method"):
            self._putback()
            return False

        self._xml_open("subroutineDec")
        self._xml(TT_KEYWORD, kw)
        func_type = kw

        self._advance()
        tt = self.tokenizer.get_token_type()
        if tt == TT_KEYWORD:
            self._xml(TT_KEYWORD, self.tokenizer.get_keyword())
        elif tt == TT_IDENTIFIER:
            self._xml(TT_IDENTIFIER, self.tokenizer.get_identifier())
        else:
            self.tokenizer.throw_exception("Expected return type")

        if func_type == "method":
            self.symbol_table.define("this", self.class_name, KIND_ARG)

        subroutine_name = self._expect_identifier("none")
        self._expect_symbol('(')
        self._xml_open("parameterList")
        self._compile_parameter_list()
        self._xml_close("parameterList")
        self._expect_symbol(')')

        self._xml_open("subroutineBody")
        self._expect_symbol('{')

        total_locals = 0
        while True:
            cnt = self._compile_var_dec()
            if cnt == 0:
                break
            total_locals += cnt

        self.vm_writer.write_function(self._full_name(subroutine_name), total_locals)

        if func_type == "constructor":
            field_count = self.symbol_table.var_count(KIND_FIELD)
            self.vm_writer.write_push(SEG_CONST, field_count)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop(SEG_POINTER, 0)
        elif func_type == "method":
            self.vm_writer.write_push(SEG_ARG, 0)
            self.vm_writer.write_pop(SEG_POINTER, 0)

        self._compile_statements()
        self._expect_symbol('}')
        self._xml_close("subroutineBody")
        self._xml_close("subroutineDec")
        return True

    def _compile_parameter_list(self):
        """((type varName) (','type varName)*)?"""
        type_expected = False
        while True:
            self._advance()
            tt = self.tokenizer.get_token_type()

            if tt == TT_KEYWORD and self.tokenizer.get_keyword() in ("int", "char", "boolean"):
                var_type = self.tokenizer.get_keyword()
                self._xml(TT_KEYWORD, var_type)
            elif tt == TT_IDENTIFIER:
                var_type = self.tokenizer.get_identifier()
                self._xml(TT_IDENTIFIER, var_type)
            elif type_expected:
                self.tokenizer.throw_exception("Expected type after ','")
            else:
                self._putback()
                return

            self._expect_identifier("declaration", var_type, KIND_ARG)

            self._advance()
            if self.tokenizer.get_token_type() == TT_SYMBOL and self.tokenizer.get_symbol() == ',':
                self._xml(TT_SYMBOL, ',')
                type_expected = True
            else:
                self._putback()
                return

    def _compile_var_dec(self):
        """'var' type varName (','varName)* ';'"""
        self._advance()
        if not (self.tokenizer.get_token_type() == TT_KEYWORD and
                self.tokenizer.get_keyword() == "var"):
            self._putback()
            return 0

        self._xml_open("varDec")
        self._xml(TT_KEYWORD, "var")
        count = 0

        var_type = self._compile_type()
        self._expect_identifier("declaration", var_type, KIND_LOCAL)
        count += 1

        while True:
            self._advance()
            if self.tokenizer.get_token_type() == TT_SYMBOL and self.tokenizer.get_symbol() == ',':
                self._xml(TT_SYMBOL, ',')
                self._expect_identifier("declaration", var_type, KIND_LOCAL)
                count += 1
            else:
                self._putback()
                break

        self._expect_symbol(';')
        self._xml_close("varDec")
        return count

    def _compile_statements(self):
        self._xml_open("statements")
        while True:
            if not (self._compile_do() or self._compile_let() or
                    self._compile_while() or self._compile_if() or
                    self._compile_return()):
                break
        self._xml_close("statements")

    def _compile_do(self):
        self._advance()
        if not (self.tokenizer.get_token_type() == TT_KEYWORD and
                self.tokenizer.get_keyword() == "do"):
            self._putback()
            return False

        self._xml_open("doStatement")
        self._xml(TT_KEYWORD, "do")

        identifier = self._expect_identifier("none")
        self._advance()
        sym = self.tokenizer.get_symbol() if self.tokenizer.get_token_type() == TT_SYMBOL else None

        if sym == '(':
            self._xml(TT_SYMBOL, '(')
            self.vm_writer.write_push(SEG_POINTER, 0)
            args = self._compile_expression_list()
            self._expect_symbol(')')
            self.vm_writer.write_call(self._full_name(identifier), args + 1)
        elif sym == '.':
            self._xml(TT_SYMBOL, '.')
            method_name = self._expect_identifier("none")
            self._expect_symbol('(')
            var_kind = self.symbol_table.kind_of(identifier)
            this_cnt = 0
            if var_kind == KIND_NONE:
                obj_name = identifier
            else:
                obj_name = self.symbol_table.type_of(identifier)
                self.vm_writer.write_push(_segment_of(var_kind), self.symbol_table.index_of(identifier))
                this_cnt = 1
            args = self._compile_expression_list()
            self._expect_symbol(')')
            self.vm_writer.write_call(f"{obj_name}.{method_name}", args + this_cnt)
        else:
            self.tokenizer.throw_exception("Expected '(' or '.' in do statement")

        self.vm_writer.write_pop(SEG_TEMP, 0)
        self._expect_symbol(';')
        self._xml_close("doStatement")
        return True

    def _compile_let(self):
        self._advance()
        if not (self.tokenizer.get_token_type() == TT_KEYWORD and
                self.tokenizer.get_keyword() == "let"):
            self._putback()
            return False

        self._xml_open("letStatement")
        self._xml(TT_KEYWORD, "let")

        identifier = self._expect_identifier("none")
        var_kind = self.symbol_table.kind_of(identifier)
        idx = self.symbol_table.index_of(identifier)

        is_array = False
        self._advance()
        if self.tokenizer.get_token_type() == TT_SYMBOL and self.tokenizer.get_symbol() == '[':
            is_array = True
            self._xml(TT_SYMBOL, '[')
            self.vm_writer.write_push(_segment_of(var_kind), idx)
            if not self._compile_expression():
                self.tokenizer.throw_exception("Expected expression in array index")
            self._expect_symbol(']')
            self.vm_writer.write_arithmetic(OP_ADD)
        else:
            self._putback()

        self._expect_symbol('=')
        if not self._compile_expression():
            self.tokenizer.throw_exception("Expected expression on right side of let")
        self._expect_symbol(';')

        if is_array:
            self.vm_writer.write_pop(SEG_TEMP, 0)
            self.vm_writer.write_pop(SEG_POINTER, 1)
            self.vm_writer.write_push(SEG_TEMP, 0)
            self.vm_writer.write_pop(SEG_THAT, 0)
        else:
            self.vm_writer.write_pop(_segment_of(var_kind), idx)

        self._xml_close("letStatement")
        return True

    def _compile_while(self):
        self._advance()
        if not (self.tokenizer.get_token_type() == TT_KEYWORD and
                self.tokenizer.get_keyword() == "while"):
            self._putback()
            return False

        self._xml_open("whileStatement")
        self._xml(TT_KEYWORD, "while")

        begin_label = self._gen_label()
        end_label = self._gen_label()

        self.vm_writer.write_label(begin_label)
        self._expect_symbol('(')
        if not self._compile_expression():
            self.tokenizer.throw_exception("Expected expression in while")
        self._expect_symbol(')')
        self.vm_writer.write_arithmetic(OP_NOT)
        self.vm_writer.write_if_goto(end_label)

        self._expect_symbol('{')
        self._compile_statements()
        self._expect_symbol('}')

        self.vm_writer.write_goto(begin_label)
        self.vm_writer.write_label(end_label)
        self._xml_close("whileStatement")
        return True

    def _compile_return(self):
        self._advance()
        if not (self.tokenizer.get_token_type() == TT_KEYWORD and
                self.tokenizer.get_keyword() == "return"):
            self._putback()
            return False

        self._xml_open("returnStatement")
        self._xml(TT_KEYWORD, "return")

        if not self._compile_expression():
            self.vm_writer.write_push(SEG_CONST, 0)

        self._expect_symbol(';')
        self.vm_writer.write_return()
        self._xml_close("returnStatement")
        return True

    def _compile_if(self):
        self._advance()
        if not (self.tokenizer.get_token_type() == TT_KEYWORD and
                self.tokenizer.get_keyword() == "if"):
            self._putback()
            return False

        self._xml_open("ifStatement")
        self._xml(TT_KEYWORD, "if")

        else_label = self._gen_label()
        end_label = self._gen_label()

        self._expect_symbol('(')
        if not self._compile_expression():
            self.tokenizer.throw_exception("Expected expression in if")
        self._expect_symbol(')')
        self.vm_writer.write_arithmetic(OP_NOT)
        self.vm_writer.write_if_goto(else_label)

        self._expect_symbol('{')
        self._compile_statements()
        self._expect_symbol('}')
        self.vm_writer.write_goto(end_label)

        self.vm_writer.write_label(else_label)
        self._advance()
        if (self.tokenizer.get_token_type() == TT_KEYWORD and
                self.tokenizer.get_keyword() == "else"):
            self._xml(TT_KEYWORD, "else")
            self._expect_symbol('{')
            self._compile_statements()
            self._expect_symbol('}')
        else:
            self._putback()

        self.vm_writer.write_label(end_label)
        self._xml_close("ifStatement")
        return True

    def _compile_expression_list(self):
        self._xml_open("expressionList")
        args = 0
        if self._compile_expression():
            args = 1
            while True:
                self._advance()
                if self.tokenizer.get_token_type() == TT_SYMBOL and self.tokenizer.get_symbol() == ',':
                    self._xml(TT_SYMBOL, ',')
                    if not self._compile_expression():
                        self.tokenizer.throw_exception("Expected expression after ','")
                    args += 1
                else:
                    self._putback()
                    break
        self._xml_close("expressionList")
        return args

    def _compile_expression(self):
        """expression: term (op term)*"""
        if not self._is_next_term():
            return False

        self._xml_open("expression")
        self._compile_term()

        while self._is_next_op():
            self._advance()
            op = self.tokenizer.get_symbol()
            self._xml(TT_SYMBOL, op)
            self._compile_term()
            self._write_op(op)

        self._xml_close("expression")
        return True

    def _compile_term(self):
        self._xml_open("term")
        self._advance()
        tt = self.tokenizer.get_token_type()

        if tt == TT_INT_CONST:
            val = self.tokenizer.get_int_val()
            self._xml(TT_INT_CONST, val)
            self.vm_writer.write_push(SEG_CONST, val)

        elif tt == TT_STRING_CONST:
            s = self.tokenizer.get_string_val()
            self._xml(TT_STRING_CONST, s)
            self.vm_writer.write_push(SEG_CONST, len(s))
            self.vm_writer.write_call("String.new", 1)
            for ch in s:
                self.vm_writer.write_push(SEG_CONST, ord(ch))
                self.vm_writer.write_call("String.appendChar", 2)

        elif tt == TT_KEYWORD and self.tokenizer.get_keyword() in ("true", "false", "null", "this"):
            kw = self.tokenizer.get_keyword()
            self._xml(TT_KEYWORD, kw)
            if kw in ("false", "null"):
                self.vm_writer.write_push(SEG_CONST, 0)
            elif kw == "true":
                self.vm_writer.write_push(SEG_CONST, 0)
                self.vm_writer.write_arithmetic(OP_NOT)
            elif kw == "this":
                self.vm_writer.write_push(SEG_POINTER, 0)

        elif tt == TT_SYMBOL and self.tokenizer.get_symbol() == '(':
            self._xml(TT_SYMBOL, '(')
            self._compile_expression()
            self._expect_symbol(')')

        elif tt == TT_SYMBOL and self.tokenizer.get_symbol() in ('-', '~'):
            sym = self.tokenizer.get_symbol()
            self._xml(TT_SYMBOL, sym)
            self._compile_term()
            self.vm_writer.write_arithmetic(OP_NEG if sym == '-' else OP_NOT)

        elif tt == TT_IDENTIFIER:
            identifier = self.tokenizer.get_identifier()
            self._xml(TT_IDENTIFIER, identifier)
            var_kind = self.symbol_table.kind_of(identifier)
            var_idx = self.symbol_table.index_of(identifier)

            self._advance()
            tt2 = self.tokenizer.get_token_type()
            sym2 = self.tokenizer.get_symbol() if tt2 == TT_SYMBOL else None

            if sym2 == '[':
                self._xml(TT_SYMBOL, '[')
                self.vm_writer.write_push(_segment_of(var_kind), var_idx)
                self._compile_expression()
                self._expect_symbol(']')
                self.vm_writer.write_arithmetic(OP_ADD)
                self.vm_writer.write_pop(SEG_POINTER, 1)
                self.vm_writer.write_push(SEG_THAT, 0)

            elif sym2 == '.':
                self._xml(TT_SYMBOL, '.')
                method_name = self._expect_identifier("none")
                self._expect_symbol('(')
                this_cnt = 0
                if var_kind == KIND_NONE:
                    obj_name = identifier
                else:
                    obj_name = self.symbol_table.type_of(identifier)
                    self.vm_writer.write_push(_segment_of(var_kind), var_idx)
                    this_cnt = 1
                args = self._compile_expression_list()
                self._expect_symbol(')')
                self.vm_writer.write_call(f"{obj_name}.{method_name}", args + this_cnt)

            elif sym2 == '(':
                self._xml(TT_SYMBOL, '(')
                self.vm_writer.write_push(SEG_POINTER, 0)
                args = self._compile_expression_list()
                self._expect_symbol(')')
                self.vm_writer.write_call(self._full_name(identifier), args + 1)

            else:
                self._putback()
                self.vm_writer.write_push(_segment_of(var_kind), var_idx)

        else:
            self.tokenizer.throw_exception("Expected term")

        self._xml_close("term")