"""
Hybrid HTTP client that can use either httpx or Rust implementation
"""
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from .rust_client import RustHttpClientWrapper

import httpx
import structlog

try:
    from .rust_client import create_rust_client
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

    def create_rust_client() -> Optional['RustHttpClientWrapper']:
        return None

logger = structlog.get_logger(__name__)


class HybridHttpClient:
    """HTTP client that can use either Rust or httpx backend"""

    def __init__(self, timeout: Union[int, float] = 30, use_rust: Optional[bool] = None):
        """Initialize the hybrid HTTP client

        Args:
            timeout: Request timeout in seconds
            use_rust: Force use of Rust client (None = auto-detect)
        """
        self.timeout = timeout

        # Determine which client to use
        if use_rust is None:
            self.use_rust = RUST_AVAILABLE
        else:
            self.use_rust = use_rust and RUST_AVAILABLE

        # Initialize clients
        self._rust_client: Optional[RustHttpClientWrapper] = None
        self._httpx_client: Optional[httpx.AsyncClient] = None

        logger.info(
            "Initialized hybrid HTTP client",
            use_rust=self.use_rust,
            rust_available=RUST_AVAILABLE
        )

    async def connect(self) -> None:
        """Initialize the HTTP client"""
        if self.use_rust:
            try:
                self._rust_client = create_rust_client()
                logger.info("Using Rust HTTP client for enhanced performance")
            except Exception as e:
                logger.warning("Failed to initialize Rust client, falling back to httpx", error=str(e))
                self.use_rust = False

        if not self.use_rust:
            self._httpx_client = httpx.AsyncClient(
                headers={"User-Agent": "PyAIBridge/1.0"},
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            )
            logger.info("Using httpx HTTP client")

    async def disconnect(self) -> None:
        """Close the HTTP client"""
        if self._httpx_client:
            await self._httpx_client.aclose()
            self._httpx_client = None

    async def post(
        self,
        url: str,
        json_data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
        stream: bool = False
    ) -> Union[dict[str, Any], AsyncGenerator[str, None]]:
        """Make a POST request

        Args:
            url: Request URL
            json_data: JSON data to send
            headers: Request headers
            timeout: Request timeout (overrides default)
            stream: Whether to stream the response

        Returns:
            Response data or async generator for streaming
        """
        if self.use_rust and self._rust_client:
            return await self._post_rust(url, json_data, headers, timeout, stream)
        else:
            return await self._post_httpx(url, json_data, headers, timeout, stream)

    async def get(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> dict[str, Any]:
        """Make a GET request

        Args:
            url: Request URL
            headers: Request headers
            timeout: Request timeout (overrides default)

        Returns:
            Response data
        """
        if self.use_rust and self._rust_client:
            return await self._get_rust(url, headers, timeout)
        else:
            return await self._get_httpx(url, headers, timeout)

    async def _post_rust(
        self,
        url: str,
        json_data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
        stream: bool = False
    ) -> Union[dict[str, Any], AsyncGenerator[str, None]]:
        """POST request using Rust client"""
        if stream:
            # For streaming, return the response body as chunks
            # Currently Rust client returns full response, so we'll simulate streaming
            assert self._rust_client is not None
            response = await self._rust_client.post(
                url=url,
                json_data=json_data,
                headers=headers,
                timeout=int(timeout or self.timeout),
                stream=stream
            )
            # Convert to async generator for compatibility
            async def _simulate_stream() -> AsyncGenerator[str, None]:
                yield response['body']
            return _simulate_stream()
        else:
            assert self._rust_client is not None
            response = await self._rust_client.post(
                url=url,
                json_data=json_data,
                headers=headers,
                timeout=int(timeout or self.timeout),
                stream=stream
            )

            return {
                'status_code': response['status'],
                'headers': response['headers'],
                'text': response['body'],
                'json': response['json']
            }

    async def _get_rust(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> dict[str, Any]:
        """GET request using Rust client"""
        assert self._rust_client is not None
        response = await self._rust_client.get(
            url=url,
            headers=headers,
            timeout=int(timeout or self.timeout)
        )

        return {
            'status_code': response['status'],
            'headers': response['headers'],
            'text': response['body'],
            'json': response['json']
        }

    async def _post_httpx(
        self,
        url: str,
        json_data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
        stream: bool = False
    ) -> Union[dict[str, Any], AsyncGenerator[str, None]]:
        """POST request using httpx client"""
        request_timeout = timeout or self.timeout

        if stream:
            return self._stream_httpx(url, json_data, headers, int(request_timeout))

        assert self._httpx_client is not None
        response = await self._httpx_client.post(
            url,
            json=json_data,
            headers=headers,
            timeout=request_timeout
        )

        try:
            json_response = response.json()
        except Exception:
            json_response = None

        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'text': response.text,
            'json': json_response
        }

    async def _get_httpx(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> dict[str, Any]:
        """GET request using httpx client"""
        assert self._httpx_client is not None
        response = await self._httpx_client.get(
            url,
            headers=headers,
            timeout=timeout or self.timeout
        )

        try:
            json_response = response.json()
        except Exception:
            json_response = None

        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'text': response.text,
            'json': json_response
        }

    async def _stream_httpx(
        self,
        url: str,
        json_data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response using httpx"""
        assert self._httpx_client is not None
        async with self._httpx_client.stream(
            "POST",
            url,
            json=json_data,
            headers=headers,
            timeout=timeout or self.timeout
        ) as response:
            async for chunk in response.aiter_text():
                yield chunk
