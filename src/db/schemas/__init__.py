#!/usr/bin/env python3
from importlib import import_module
from os import listdir
from pathlib import Path

# Path(__file__) is src/db/schema/__init__.py, while
# Path(__file__).parent is src/db/schema
package_dir = Path(__file__).parent

for file in package_dir.iterdir():
    if file.is_file() and file.name.endswith(".py") and not file.name.startswith("__"):
        import_module(f"{__name__}.{file.stem}")
