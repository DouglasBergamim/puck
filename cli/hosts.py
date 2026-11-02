"""Host configuration: the HostConfig files under hosts/."""

from pathlib import Path

import yaml

from cli import store


def load(root: Path | None = None) -> dict[str, dict]:
    directory = (root or store.home()) / "hosts"
    configs = (yaml.safe_load(p.read_text()) for p in sorted(directory.glob("*.yaml")))
    return {config["name"]: config for config in configs}


def canonical_tool(config: dict, name: str) -> str:
    """Map a host's tool name to a Puck capability."""
    for capability, tools in config.get("capabilities", {}).items():
        if name in tools:
            return capability
    return name.lower()
