from .parser_setup import parser
from .functions_extractor import extract_functions
from .classes_extractor import extract_classes
from .imports_extractor import extract_imports
from .globals_extractor import extract_global_variables
from .inputs_extractor import extract_input_sources


def analyze_code(code: str):
    code_bytes = code.encode("utf-8")
    tree = parser.parse(code_bytes)
    root_node = tree.root_node

    functions = extract_functions(root_node, code_bytes)
    classes = extract_classes(root_node, code_bytes)
    imports = extract_imports(root_node, code_bytes)
    globals_list = extract_global_variables(root_node, code_bytes)
    input_sources = extract_input_sources(root_node, code_bytes)

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "global_variables": globals_list,
        "input_sources": input_sources
    }

if __name__ == "__main__":
    sample_code = """
import os
from flask import request

SECRET_KEY = "hardcoded"

class User:
    def login(self):
        username = request.args.get("user")

def main():
    password = input("Enter password")
"""

    result = analyze_code(sample_code)
    import json
    print(json.dumps(result, indent=2))