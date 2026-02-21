def extract_dangerous_sinks(node, code_bytes, sinks=None):
    if sinks is None:
        sinks = []

    # Detect function calls
    if node.type == "call":
        function_node = node.child_by_field_name("function")
        if function_node:
            function_name = code_bytes[
                function_node.start_byte:function_node.end_byte
            ].decode("utf-8")

            dangerous_functions = [
                "eval",
                "exec",
                "os.system",
                "subprocess.run",
                "subprocess.call",
                "subprocess.Popen",
                "pickle.loads",
                "cursor.execute"
            ]

            if function_name in dangerous_functions:
                sinks.append({
                    "type": function_name,
                    "line": node.start_point[0] + 1
                })

    for child in node.children:
        extract_dangerous_sinks(child, code_bytes, sinks)

    return sinks