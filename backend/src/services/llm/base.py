from typing import Protocol


class LLMClient(Protocol):
	"""Abstract LLM client interface."""

	def generate(self, prompt: str, *, timeout: float | None = None) -> str:
		"""Generate a completion for the given prompt and return raw text."""
		...