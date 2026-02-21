def extract_input_sources(node, code_bytes, inputs=None):
    if inputs is None:
        inputs = []

    # Detect function calls like input()
    if node.type == "call":
        function_node = node.child_by_field_name("function")
        if function_node and function_node.type == "attribute":
            full_name = code_bytes[
                function_node.start_byte:function_node.end_byte
            ].decode("utf-8")

            if full_name.startswith("request.args"):
                inputs.append({
                    "type": full_name,
                    "line": node.start_point[0] + 1
                })

    # Detect attribute access like request.args, os.environ
    if node.type == "attribute":
        value_node = node.child_by_field_name("value")
        attr_node = node.child_by_field_name("attribute")

        if value_node and attr_node:
            value = code_bytes[value_node.start_byte:value_node.end_byte].decode("utf-8")
            attr = code_bytes[attr_node.start_byte:attr_node.end_byte].decode("utf-8")

            full_attr = f"{value}.{attr}"

            if full_attr in ["request.args", "request.form", "request.json", "os.environ", "sys.argv"]:
                inputs.append({
                    "type": full_attr,
                    "line": node.start_point[0] + 1
                })

    for child in node.children:
        extract_input_sources(child, code_bytes, inputs)

    return inputs