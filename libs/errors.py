class ToolError(Exception):
    """Base for anything an MCP server raises."""


class ApiError(ToolError):
    """Non-2xx response or timeout from an external API."""


class RateLimitedError(ApiError):
    """HTTP 429 from an external API."""

class UnknownProviderError(ToolError):
    """Unknown provider LLM Model."""
