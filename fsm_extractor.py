import ast
import sys


class FSMExtractor(ast.NodeVisitor):
    def __init__(self, state_var="state"):
        self.constants = {}
        self.transitions = []
        self.current_state_context = None
        self.state_var = state_var

    def visit_Assign(self, node):
        # capture constants like STATE_ARMING = "ARMING"
        if isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            value = node.value
            if isinstance(value, ast.Constant):
                self.constants[name] = value.value

        # detect: state = ...
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == self.state_var:
                next_state = self._resolve_value(node.value)
                if self.current_state_context:
                    src_states, trigger = self.current_state_context
                    if isinstance(src_states, list):
                        for src in src_states:
                            self.transitions.append((src, next_state, trigger))
                    else:
                        self.transitions.append((src_states, next_state, trigger))
        self.generic_visit(node)

    def visit_If(self, node):
        src_states, trigger = self._extract_fsm_condition(node.test)

        # if outer condition is state == ... or state in (...), set context
        if src_states and not trigger:
            for src in src_states if isinstance(src_states, list) else [src_states]:
                self.transitions.append((src, src, "active block"))
            self.current_state_context = (src_states, None)
            for stmt in node.body:
                self.visit(stmt)
            for stmt in node.orelse:
                self.visit(stmt)
            self.current_state_context = None
        elif src_states:
              # simple short state block with one condition
              self.current_state_context = (src_states, trigger)
              for stmt in node.body:
                  self.visit(stmt)
              for stmt in node.orelse:
                  self.visit(stmt)
              self.current_state_context = None
        else:
            # Nested condition inside a known state block
            if self.current_state_context:
                self.current_state_context = (self.current_state_context[0], trigger)
                for stmt in node.body:
                    self.visit(stmt)
                for stmt in node.orelse:
                    self.visit(stmt)
                if self.current_state_context:
                    self.current_state_context = (self.current_state_context[0], None)
            else:
                for stmt in node.body:
                    self.visit(stmt)
                for stmt in node.orelse:
                    self.visit(stmt)

    def _extract_fsm_condition(self, test):
        state_context = []
        triggers = []

        def extract(expr):
            s, t = self._extract_fsm_condition(expr)
            if s:
                state_context.extend(s if isinstance(s, list) else [s])
            if t:
                triggers.append(t)

        if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And):
            for expr in test.values:
                extract(expr)

        elif isinstance(test, ast.Compare):
            if isinstance(test.left, ast.Name) and test.left.id == self.state_var:
                comparator = test.comparators[0]
                if isinstance(comparator, ast.Tuple):
                    state_context = [self._resolve_value(e) for e in comparator.elts]
                else:
                    state_context = [self._resolve_value(comparator)]
            else:
                triggers.append(self._extract_compare_repr(test))

        elif isinstance(test, ast.Call):
            triggers.append(self._extract_call_repr(test))

        elif isinstance(test, ast.Name):
            triggers.append(test.id)

        return state_context if state_context else None, " and ".join(triggers) if triggers else None


    def _extract_call_repr(self, call):
        if isinstance(call.func, ast.Name):
            return f"{call.func.id}()"
        elif isinstance(call.func, ast.Attribute):
            return f"{call.func.value.id}.{call.func.attr}()"
        return "trigger"

    def _extract_compare_repr(self, cmp):
        try:
            return ast.unparse(cmp)
        except Exception:
            left = self._expr_to_str(cmp.left)
            right = self._expr_to_str(cmp.comparators[0])
            op = self._op_to_str(cmp.ops[0])
            return f"{left} {op} {right}"

    def _expr_to_str(self, expr):
        if isinstance(expr, ast.Name):
            return expr.id
        elif isinstance(expr, ast.Call):
            return self._extract_call_repr(expr)
        elif isinstance(expr, ast.BinOp):
            left = self._expr_to_str(expr.left)
            right = self._expr_to_str(expr.right)
            op = self._op_to_str(expr.op)
            return f"({left} {op} {right})"
        elif isinstance(expr, ast.Constant):
            return str(expr.value)
        return "expr"

    def _op_to_str(self, op):
        return {
            ast.Gt: ">",
            ast.Lt: "<",
            ast.Eq: "==",
            ast.NotEq: "!=",
            ast.GtE: ">=",
            ast.LtE: "<=",
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.Mod: "%",
            ast.And: "and",
            ast.Or: "or",
            ast.BitAnd: "&",
            ast.BitOr: "|",
            ast.RShift: ">>",
            ast.LShift: "<<",
        }.get(type(op), "?")

    def _resolve_value(self, node_or_name):
        if isinstance(node_or_name, ast.Name):
            return self.constants.get(node_or_name.id, node_or_name.id)
        elif isinstance(node_or_name, str):
            return self.constants.get(node_or_name, node_or_name)
        elif isinstance(node_or_name, ast.Constant):
            return node_or_name.value
        return None
