# inputs_extractor.py

def extract_input_sources(node, code_bytes, inputs=None):
    if inputs is None:
        inputs = []

    # Helper to decode node text
    def get_text(n):
        return code_bytes[n.start_byte:n.end_byte].decode("utf-8")

    # 1️⃣ Detect input()
    if node.type == "call":
        function_node = node.child_by_field_name("function")
        if function_node:
            func_text = get_text(function_node)

            if func_text == "input":
                inputs.append({
                    "type": "input()",
                    "line": node.start_point[0] + 1
                })

    # 2️⃣ Detect attribute chains (request.args, os.environ, etc.)
    if node.type == "attribute":
        value_node = node.child_by_field_name("value")
        attr_node = node.child_by_field_name("attribute")

        if value_node and attr_node:
            value_text = get_text(value_node)
            attr_text = get_text(attr_node)

            full_attr = f"{value_text}.{attr_text}"

            if full_attr in [
                "request.args",
                "request.form",
                "request.json",
                "os.environ",
            ]:
                inputs.append({
                    "type": full_attr,
                    "line": node.start_point[0] + 1
                })

    # 3️⃣ Detect sys.argv (subscript)
    if node.type == "subscript":
        value_node = node.child_by_field_name("value")
        if value_node:
            value_text = get_text(value_node)

            if value_text == "sys.argv":
                inputs.append({
                    "type": "sys.argv",
                    "line": node.start_point[0] + 1
                })

    # 4️⃣ Detect chained calls like request.args.get()
    if node.type == "call":
        function_node = node.child_by_field_name("function")
        if function_node and function_node.type == "attribute":
            full_text = get_text(function_node)

            if full_text.startswith("request.args"):
                inputs.append({
                    "type": full_text,
                    "line": node.start_point[0] + 1
                })

            if full_text.startswith("request.form"):
                inputs.append({
                    "type": full_text,
                    "line": node.start_point[0] + 1
                })

            if full_text.startswith("os.environ"):
                inputs.append({
                    "type": full_text,
                    "line": node.start_point[0] + 1
                })

    # Recursive traversal
    for child in node.children:
        extract_input_sources(child, code_bytes, inputs)

    return inputs