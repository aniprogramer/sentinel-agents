def extract_functions(node, code_bytes, functions=None):
    if functions is None:
        functions = []

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