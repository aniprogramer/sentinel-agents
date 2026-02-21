# globals_extractor.py

def extract_global_variables(node, code_bytes, globals_list=None):
    if globals_list is None:
        globals_list = []

    def get_text(n):
        return code_bytes[n.start_byte:n.end_byte].decode("utf-8")

    def extract_identifiers_from_assignment(assign_node):
        names = []

        # Left side of assignment
        left = assign_node.children[0]

        # If simple identifier
        if left.type == "identifier":
            names.append(get_text(left))

        # If tuple unpacking
        elif left.type in ["tuple", "pattern_list"]:
            for child in left.children:
                if child.type == "identifier":
                    names.append(get_text(child))

        # 🔥 NEW: Check if right side is another assignment (chained)
        right = assign_node.children[-1]
        if right.type == "assignment":
            names.extend(extract_identifiers_from_assignment(right))

        return names

    if node.type == "assignment":
        if (
            node.parent
            and node.parent.parent
            and node.parent.parent.type == "module"
        ):
            identifiers = extract_identifiers_from_assignment(node)

            for name in identifiers:
                globals_list.append({
                    "name": name,
                    "line": node.start_point[0] + 1
                })

    for child in node.children:
        extract_global_variables(child, code_bytes, globals_list)

    return globals_list