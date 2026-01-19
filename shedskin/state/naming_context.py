# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.state.naming_context: Naming conventions and reserved words."""

from dataclasses import dataclass, field
from typing import List, Set


@dataclass(frozen=True)
class NamingContext:
    """Immutable naming context for C++ code generation.

    Attributes:
        cpp_keywords: Set of C++ reserved keywords to avoid.
        ss_prefix: Prefix used for shedskin-generated identifiers.
        builtins: List of builtin type names.
    """

    cpp_keywords: Set[str] = field(default_factory=set)
    ss_prefix: str = "__ss_"
    builtins: List[str] = field(
        default_factory=lambda: [
            "none",
            "str_",
            "bytes_",
            "float_",
            "int_",
            "class_",
            "list",
            "tuple",
            "tuple2",
            "dict",
            "set",
            "frozenset",
            "bool_",
        ]
    )
