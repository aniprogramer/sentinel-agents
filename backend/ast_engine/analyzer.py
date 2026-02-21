from parser_setup import parser
from functions_extractor import extract_functions
from classes_extractor import extract_classes
from imports_extractor import extract_imports
from globals_extractor import extract_global_variables
from inputs_extractor import extract_input_sources
from sinks_extractor import extract_dangerous_sinks

def deduplicate(items):
    seen = set()
    unique = []
    for item in items:
        key = (item["type"], item["line"])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def analyze_code(code: str):
    if len(code) > 200_000:
        return {
            "error": "File too large"
        }
    
    code_bytes = code.encode("utf-8")

    try:
        tree = parser.parse(code_bytes)
    except Exception as e:
        return {
            "error": "Parsing failed",
            "details": str(e)
        }
    
    root_node = tree.root_node

    functions = extract_functions(root_node, code_bytes)
    classes = extract_classes(root_node, code_bytes)
    imports = extract_imports(root_node, code_bytes)
    globals_list = extract_global_variables(root_node, code_bytes)
    input_sources = extract_input_sources(root_node, code_bytes)
    dangerous_sinks = extract_dangerous_sinks(root_node, code_bytes)
    input_sources = deduplicate(input_sources)
    dangerous_sinks = deduplicate(dangerous_sinks)

    # Simple risk scoring
    risk_score = len(input_sources) * 2 + len(dangerous_sinks) * 3

    if risk_score >= 5:
        risk_level = "HIGH"
    elif risk_score >= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"


    summary = {
        "total_functions": len(functions),
        "total_classes": len(classes),
        "total_imports": len(imports),
        "total_inputs": len(input_sources),
        "total_sinks": len(dangerous_sinks),
        "risk_level": risk_level
    }

    # 🔹 Build detailed section
    details = {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "global_variables": globals_list,
        "input_sources": input_sources,
        "dangerous_sinks": dangerous_sinks
    }

    return {
        "summary": summary,
        "details": details
    }

if __name__ == "__main__":
    import json
    import os

    file_path = os.path.join("..", "test_files", "sample_vulnerable.py")

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    result = analyze_code(code)

    print(json.dumps(result, indent=2))