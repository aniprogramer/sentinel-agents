from tree_sitter import Parser, Language
from tree_sitter_python import language as python_capsule

PY_LANGUAGE = Language(python_capsule())

parser = Parser()
parser.language = PY_LANGUAGE