"""
Rust-accelerated HTTP client for PyAIBridge
"""
import json
from typing import Any, Optional

try:
    from .pyaibridge_core import (  # type: ignore[import-untyped]  # noqa: I001
        HttpClient as RustHttpClient,
        HttpResponse,
    )
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    RustHttpClient = None
    HttpResponse = None


class RustHttpClientWrapper:
    """Wrapper around the Rust HTTP client to provide a Python-friendly interface"""

    def __init__(self) -> None:
        if not RUST_AVAILABLE:
            raise ImportError("Rust extension not available. Please build with maturin.")
        self._client = RustHttpClient()

    async def post(
        self,
        url: str,
        json_data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
        stream: bool = False
    ) -> dict[str, Any]:
        """Make a POST request with JSON data"""
        try:
            if stream:
                # Use the post_stream method for streaming requests
                response = await self._client.post_stream(url, json_data, headers, timeout)
            else:
                response = await self._client.post(url, json_data, headers, timeout)

            return {
                'status': response.status,
                'headers': response.headers,
                'body': response.body,
                'json': self._try_parse_json(response.body)
            }
        except Exception as e:
            raise RuntimeError(f"HTTP request failed: {e}") from e

    async def get(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> dict[str, Any]:
        """Make a GET request"""
        try:
            response = await self._client.get(url, headers, timeout)
            return {
                'status': response.status,
                'headers': response.headers,
                'body': response.body,
                'json': self._try_parse_json(response.body)
            }
        except Exception as e:
            raise RuntimeError(f"HTTP request failed: {e}") from e

    def _try_parse_json(self, body: str) -> Optional[dict[str, Any]]:
        """Try to parse JSON response body"""
        try:
            return json.loads(body)
        except (json.JSONDecodeError, ValueError):
            return None


def create_rust_client() -> Optional[RustHttpClientWrapper]:
    """Create a Rust HTTP client if available"""
    if not RUST_AVAILABLE:
        return None
    return RustHttpClientWrapper()
