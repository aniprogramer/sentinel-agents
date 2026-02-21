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