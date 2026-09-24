import os
from abc import ABC, abstractmethod

import httpx
from dotenv import load_dotenv

load_dotenv()


class ToolError(Exception):
    """Base for anything an MCP server raises."""


class ApiError(ToolError):
    """Non-2xx response or timeout from an external API."""


class RateLimitedError(ApiError):
    """HTTP 429 from an external API."""


class ApiToolServer(ABC):
    def __init__(self, name: str, key_env: str, timeout: float = 10.0):
        self.name = name
        self.key = os.environ[key_env]          # fails at construction if missing
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    @property
    @abstractmethod
    def base_url(self) -> str: ...

    async def get(self, path: str, **params) -> dict | list:
        params["appid"] = self.key              # OpenWeather-specific; see NOTES.md
        try:
            resp = await self.client.get(path, params=params)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitedError(f"{self.name}: rate limited") from e
            raise ApiError(f"{self.name}: HTTP {e.response.status_code}") from e
        except httpx.TimeoutException as e:
            raise ApiError(f"{self.name}: timeout on {path}") from e

    async def aclose(self) -> None:
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r}, base_url={self.base_url!r})"
