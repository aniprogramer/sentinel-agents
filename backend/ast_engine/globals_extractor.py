# globals_extractor.py

def extract_global_variables(node, code_bytes, globals_list=None):
    if globals_list is None:
        globals_list = []

    # Detect assignment nodes
    if node.type == "assignment":
        # Ensure it's module-level
        if (
            node.parent
            and node.parent.parent
            and node.parent.parent.type == "module"
        ):
            left_node = node.children[0]

            # Case 1: Single variable assignment
            if left_node.type == "identifier":
                var_name = code_bytes[
                    left_node.start_byte:left_node.end_byte
                ].decode("utf-8")

                globals_list.append({
                    "name": var_name,
                    "line": node.start_point[0] + 1
                })

            # Case 2: Tuple unpacking (a, b = ...)
            elif left_node.type == "tuple":
                for child in left_node.children:
                    if child.type == "identifier":
                        var_name = code_bytes[
                            child.start_byte:child.end_byte
                        ].decode("utf-8")

                        globals_list.append({
                            "name": var_name,
                            "line": node.start_point[0] + 1
                        })

    # Recursively traverse
    for child in node.children:
        extract_global_variables(child, code_bytes, globals_list)

    return globals_list