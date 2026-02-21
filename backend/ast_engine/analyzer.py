from tree_sitter import Parser, Language
from tree_sitter_python import language as python_capsule

PY_LANGUAGE = Language(python_capsule())

parser = Parser()
parser.language = PY_LANGUAGE

def extract_functions(node, code_bytes, functions=None):
    if functions is None:
        functions = []

    # Only capture top-level functions
    if node.type == "function_definition" and node.parent.type == "module":
        name_node = node.child_by_field_name("name")
        params_node = node.child_by_field_name("parameters")

        function_name = code_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8")

        parameters = []
        if params_node:
            for child in params_node.children:
                if child.type == "identifier":
                    param_name = code_bytes[child.start_byte:child.end_byte].decode("utf-8")
                    parameters.append(param_name)

        functions.append({
            "name": function_name,
            "parameters": parameters,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1
        })

    for child in node.children:
        extract_functions(child, code_bytes, functions)

    return functions


def analyze_code(code: str):
    code_bytes = code.encode("utf-8")
    tree = parser.parse(code_bytes)
    root_node = tree.root_node

    functions = extract_functions(root_node, code_bytes)
    classes = extract_classes(root_node, code_bytes)
    imports = extract_imports(root_node, code_bytes)
    globals_list = extract_global_variables(root_node, code_bytes)

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "global_variables": globals_list
    }


if __name__ == "__main__":
    sample_code = """
import os

SECRET_KEY = "hardcoded"
debug = True

def main():
    local_var = 10
"""

    result = analyze_code(sample_code)
    print(result)