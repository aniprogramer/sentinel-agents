from parser_setup import parser
from functions_extractor import extract_functions
from classes_extractor import extract_classes
from imports_extractor import extract_imports
from globals_extractor import extract_global_variables
from inputs_extractor import extract_input_sources
from sinks_extractor import extract_dangerous_sinks


def analyze_code(code: str):
    code_bytes = code.encode("utf-8")
    tree = parser.parse(code_bytes)
    root_node = tree.root_node

    functions = extract_functions(root_node, code_bytes)
    classes = extract_classes(root_node, code_bytes)
    imports = extract_imports(root_node, code_bytes)
    globals_list = extract_global_variables(root_node, code_bytes)
    input_sources = extract_input_sources(root_node, code_bytes)
    dangerous_sinks = extract_dangerous_sinks(root_node, code_bytes)

    risk_level = "LOW"

    if input_sources and dangerous_sinks:
        risk_level = "HIGH"
    elif input_sources or dangerous_sinks:
        risk_level = "MEDIUM"


    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "global_variables": globals_list,
        "input_sources": input_sources,
        "dangerous_sinks": dangerous_sinks,
        "risk_level": risk_level
    }

if __name__ == "__main__":
    sample_code = """
import os
import subprocess
from flask import request

SECRET_KEY = "hardcoded"

def vulnerable():
    user = request.args.get("cmd")
    os.system(user)
"""

    result = analyze_code(sample_code)
    import json
    print(json.dumps(result, indent=2))