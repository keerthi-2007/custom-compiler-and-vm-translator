INVALID_NUMBER = -1
KIND_STATIC = "static"
KIND_FIELD = "field"
KIND_ARG = "argument"
KIND_LOCAL = "local"
KIND_NONE = None
class SymbolTable:
    def __init__(self):
        self.class_table = {}      
        self.subroutine_table = {}  
        self.indices = {
            KIND_STATIC: 0,
            KIND_FIELD: 0,
            KIND_ARG: 0,
            KIND_LOCAL: 0,
        }

    def clear(self):
        self.class_table = {}
        self.subroutine_table = {}
        for k in self.indices:
            self.indices[k] = 0

    def start_subroutine(self):
        self.subroutine_table = {}
        self.indices[KIND_ARG] = 0
        self.indices[KIND_LOCAL] = 0

    def define(self, name, var_type, kind):
        index = self.indices[kind]
        self.indices[kind] += 1
        info = {"type": var_type, "kind": kind, "index": index}
        if kind in (KIND_ARG, KIND_LOCAL):
            self.subroutine_table[name] = info
        else:  
            self.class_table[name] = info

    def var_count(self, kind):
        return self.indices.get(kind, 0)

    def _get_scope(self, name):
        if name in self.subroutine_table:
            return self.subroutine_table
        if name in self.class_table:
            return self.class_table
        return None

    def kind_of(self, name):
        table = self._get_scope(name)
        return table[name]["kind"] if table else KIND_NONE

    def type_of(self, name):
        table = self._get_scope(name)
        return table[name]["type"] if table else ""

    def index_of(self, name):
        table = self._get_scope(name)
        return table[name]["index"] if table else INVALID_NUMBER