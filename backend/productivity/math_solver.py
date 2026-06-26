import math
import re

try:
    import sympy
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False


class MathSolver:
    def __init__(self):
        self.variables = {}

    def evaluate(self, expression, **variables):
        safe_dict = {"__builtins__": None, "math": math}
        safe_dict.update(math.__dict__)
        safe_dict.update(variables)
        allowed_names = {
            "abs", "round", "max", "min", "sum", "pow", "int", "float", "str", "bool",
            "len", "range", "list", "dict", "tuple", "set", "enumerate", "zip", "map",
            "filter", "any", "all", "sorted", "reversed",
        }
        for name in allowed_names:
            safe_dict[name] = __builtins__[name] if isinstance(__builtins__, dict) else getattr(__builtins__, name)
        try:
            return float(eval(expression, safe_dict))
        except Exception as e:
            raise ValueError(f"Evaluation failed: {e}")

    def solve_equation(self, equation, variable="x"):
        if HAS_SYMPY:
            x = sympy.Symbol(variable)
            expr = sympy.sympify(equation.replace("=", "-(") + ")")
            solutions = sympy.solve(expr, x)
            return [complex(sol).real if sol.is_real else complex(sol) for sol in solutions]
        raise NotImplementedError("sympy is required for equation solving. Install with: pip install sympy")

    def simplify(self, expression):
        if HAS_SYMPY:
            expr = sympy.sympify(expression)
            simplified = sympy.simplify(expr)
            return str(simplified)
        raise NotImplementedError("sympy is required for simplification")

    def differentiate(self, expression, variable="x"):
        if HAS_SYMPY:
            x = sympy.Symbol(variable)
            expr = sympy.sympify(expression)
            result = sympy.diff(expr, x)
            return str(result)
        raise NotImplementedError("sympy is required for differentiation")

    def integrate(self, expression, variable="x"):
        if HAS_SYMPY:
            x = sympy.Symbol(variable)
            expr = sympy.sympify(expression)
            result = sympy.integrate(expr, x)
            return str(result)
        raise NotImplementedError("sympy is required for integration")

    def solve_linear_system(self, equations, variables=None):
        if not HAS_SYMPY:
            raise NotImplementedError("sympy is required for linear systems")
        if variables is None:
            all_vars = set()
            for eq in equations:
                all_vars.update(re.findall(r"[a-zA-Z_]\w*", eq))
            variables = sorted(all_vars)
        symbols = sympy.symbols(variables)
        parsed_eqs = [sympy.sympify(eq.replace("=", "-(") + ")") for eq in equations]
        solution = sympy.solve(parsed_eqs, symbols)
        return {str(k): float(v) if v.is_Number else str(v) for k, v in solution.items()}

    def set_variable(self, name, value):
        self.variables[name] = float(value)

    def get_variable(self, name):
        if name not in self.variables:
            raise KeyError(f"Variable '{name}' not set")
        return self.variables[name]
