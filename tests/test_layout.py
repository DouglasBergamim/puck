"""Core is layered so each part can be read and changed on its own."""

import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
LAYERS = ["core.common", "core.primitives", "core.tools.work", "core.tools.learning", "core.hooks"]
IMPORT = re.compile(r"^\s*(?:from|import)\s+(core(?:\.[a-z_]+)*)", re.MULTILINE)


def layer(module: str) -> int:
    for index, prefix in reversed(list(enumerate(LAYERS))):
        if module == prefix or module.startswith(prefix + "."):
            return index
    raise AssertionError(f"{module} belongs to no layer; add it to LAYERS")


def module_of(path: Path) -> str:
    return ".".join(path.relative_to(SRC).with_suffix("").parts)


def imports(path: Path) -> list[str]:
    found = []
    for match in IMPORT.finditer(path.read_text()):
        name = match.group(1)
        # `from core import hooks` names a module, not a package.
        line = path.read_text()[match.start():].split("\n", 1)[0]
        tail = re.match(r"\s*from\s+core\s+import\s+(\w+)", line)
        found.append(f"core.{tail.group(1)}" if tail else name)
    return found


def test_core_imports_only_downwards():
    upward = []
    for path in (SRC / "core").rglob("*.py"):
        if path.name == "__init__.py":
            continue
        own = layer(module_of(path))
        upward += [f"{module_of(path)} imports {name}" for name in imports(path) if layer(name) > own]
    assert upward == []


def test_adapters_import_only_the_model():
    others = [f"{path.name}: {name}" for path in (SRC / "adapters").rglob("*.py")
              for name in imports(path) if name != "core.common.model"]
    assert others == []
