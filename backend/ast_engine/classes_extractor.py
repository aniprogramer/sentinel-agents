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