def extract_input_sources(node, code_bytes, inputs=None):
    if inputs is None:
        inputs = []

    # Detect function calls like input()
    if node.type == "call":
        function_node = node.child_by_field_name("function")
        if function_node:
            function_name = code_bytes[
                function_node.start_byte:function_node.end_byte
            ].decode("utf-8")

            if function_name == "input":
                inputs.append({
                    "type": "input()",
                    "line": node.start_point[0] + 1
                })

    # Detect attribute access like request.args, os.environ
    if node.type == "attribute":
        attr_name = code_bytes[
            node.start_byte:node.end_byte
        ].decode("utf-8")

        if any(keyword in attr_name for keyword in [
            "request.args",
            "request.form",
            "request.json",
            "os.environ",
            "sys.argv"
        ]):
            inputs.append({
                "type": attr_name,
                "line": node.start_point[0] + 1
            })

    for child in node.children:
        extract_input_sources(child, code_bytes, inputs)

    return inputs