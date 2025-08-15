from typing import Protocol, Dict, Any


class NodeExecutor(Protocol):
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        ...