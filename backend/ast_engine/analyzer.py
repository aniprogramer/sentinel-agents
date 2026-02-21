from tree_sitter import Parser, Language
from tree_sitter_python import language as python_capsule

PY_LANGUAGE = Language(python_capsule())

parser = Parser()
parser.language = PY_LANGUAGE

def extract_imports(node, code_bytes, imports=None):
    if imports is None:
        imports = []

    if node.type == "import_statement":
        for child in node.children:
            if child.type == "dotted_name":
                module_name = code_bytes[
                    child.start_byte:child.end_byte
                ].decode("utf-8")

                imports.append({
                    "type": "import",
                    "module": module_name,
                    "line": node.start_point[0] + 1
                })

    elif node.type == "import_from_statement":
        # In tree-sitter-python, structure is:
        # from <module> import <names>
        for child in node.children:
            if child.type == "dotted_name":
                module_name = code_bytes[
                    child.start_byte:child.end_byte
                ].decode("utf-8")

                imports.append({
                    "type": "from_import",
                    "module": module_name,
                    "line": node.start_point[0] + 1
                })
                break

    for child in node.children:
        extract_imports(child, code_bytes, imports)

    return imports

def extract_global_variables(node, code_bytes, globals_list=None):
    if globals_list is None:
        globals_list = []

    # Detect assignment
    if node.type == "assignment":
        # Check if it is at module level
        if node.parent and node.parent.parent and node.parent.parent.type == "module":
            left_node = node.children[0]

            if left_node.type == "identifier":
                var_name = code_bytes[
                    left_node.start_byte:left_node.end_byte
                ].decode("utf-8")

                globals_list.append({
                    "name": var_name,
                    "line": node.start_point[0] + 1
                })

    for child in node.children:
        extract_global_variables(child, code_bytes, globals_list)

    return globals_list

def extract_classes(node, code_bytes, classes=None):
    if classes is None:
        classes = []

    if node.type == "class_definition":
        name_node = node.child_by_field_name("name")
        class_name = code_bytes[name_node.start_byte:name_node.end_byte].decode("utf-8")

        methods = []

        # Look inside class body for methods
        body_node = node.child_by_field_name("body")
        if body_node:
            for child in body_node.children:
                if child.type == "function_definition":
                    method_name_node = child.child_by_field_name("name")
                    params_node = child.child_by_field_name("parameters")

                    method_name = code_bytes[
                        method_name_node.start_byte:method_name_node.end_byte
                    ].decode("utf-8")

                    parameters = []
                    if params_node:
                        for param in params_node.children:
                            if param.type == "identifier":
                                param_name = code_bytes[
                                    param.start_byte:param.end_byte
                                ].decode("utf-8")
                                parameters.append(param_name)

                    methods.append({
                        "name": method_name,
                        "parameters": parameters,
                        "start_line": child.start_point[0] + 1,
                        "end_line": child.end_point[0] + 1
                    })

        classes.append({
            "name": class_name,
            "methods": methods,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1
        })

    # recursive traversal
    for child in node.children:
        extract_classes(child, code_bytes, classes)

    return classes


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