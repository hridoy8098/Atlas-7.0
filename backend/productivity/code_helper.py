import ast
import textwrap


class ProductivityCodeHelper:
    def __init__(self, language="python"):
        self.language = language
        self._snippets = {}

    def add_snippet(self, name, code, description=""):
        self._snippets[name] = {"code": code, "description": description}

    def get_snippet(self, name):
        snippet = self._snippets.get(name)
        if not snippet:
            raise KeyError(f"Snippet '{name}' not found")
        return snippet

    def list_snippets(self):
        return {k: v["description"] for k, v in self._snippets.items()}

    def remove_snippet(self, name):
        if name not in self._snippets:
            raise KeyError(f"Snippet '{name}' not found")
        del self._snippets[name]

    def format_code(self, code, indent=4):
        if self.language == "python":
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                raise ValueError(f"Invalid Python code: {e}")
            return ast.unparse(tree)
        return textwrap.indent(code, " " * indent)

    def check_syntax(self, code):
        if self.language != "python":
            raise NotImplementedError("Syntax checking only supported for Python")
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)

    def rename_variable(self, code, old_name, new_name):
        if self.language != "python":
            raise NotImplementedError("Refactoring only supported for Python")
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Cannot parse code: {e}")

        class Renamer(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id == old_name:
                    return ast.copy_location(ast.Name(id=new_name, ctx=node.ctx), node)
                return node

        new_tree = Renamer().visit(tree)
        ast.fix_missing_locations(new_tree)
        return ast.unparse(new_tree)

    def get_function_signature_hints(self, code):
        if self.language != "python":
            raise NotImplementedError("Hints only supported for Python")
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Cannot parse code: {e}")
        hints = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                hints.append({"name": node.name, "args": args})
        return hints
