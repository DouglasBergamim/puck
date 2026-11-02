"""The registry: the only link between core and specific harnesses."""

from adapters.base import Adapter
from adapters.claude import ClaudeAdapter
from adapters.copilot import CopilotAdapter

ADAPTERS: dict[str, Adapter] = {
    adapter.name: adapter
    for adapter in (Adapter(), ClaudeAdapter(), CopilotAdapter("cli"), CopilotAdapter("vscode"))
}
PRIMARY = "claude"


def get(name: str) -> Adapter:
    return ADAPTERS[name]


def primary() -> Adapter:
    return ADAPTERS[PRIMARY]
