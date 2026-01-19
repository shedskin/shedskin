# SHED SKIN Python-to-C++ Compiler
# Copyright 2005-2024 Mark Dufour and contributors; GNU GPL version 3 (See LICENSE)
"""shedskin.state: Focused state objects extracted from GlobalInfo.

This package contains dataclasses that encapsulate related groups of state
from the GlobalInfo class, providing better organization and cohesion.
"""

from .build_config import BuildConfiguration
from .entity_registry import EntityRegistry
from .filesystem_paths import FileSystemPaths
from .graph_context import GraphBuildingContext
from .naming_context import NamingContext
from .type_inference import TypeInferenceState

__all__ = [
    "BuildConfiguration",
    "EntityRegistry",
    "FileSystemPaths",
    "GraphBuildingContext",
    "NamingContext",
    "TypeInferenceState",
]
