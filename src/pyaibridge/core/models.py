"""Data models for pyaibridge."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class MessageRole(str, Enum):
    """Message role types."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """A chat message."""

    role: MessageRole = Field(..., description="The role of the message sender")
    content: str = Field(..., min_length=1, description="The message content")
    name: Optional[str] = Field(None, description="Optional name of the message sender")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    model_config = ConfigDict(use_enum_values=True)


class ChatRequest(BaseModel):
    """Request for chat completion."""

    messages: list[Message] = Field(..., min_length=1, description="List of messages")
    model: str = Field(..., description="Model to use for completion")
    max_tokens: Optional[int] = Field(
        None, gt=0, description="Maximum tokens to generate"
    )
    temperature: Optional[float] = Field(
        None, ge=0.0, le=2.0, description="Sampling temperature"
    )
    top_p: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Top-p sampling parameter"
    )
    frequency_penalty: Optional[float] = Field(
        None, ge=-2.0, le=2.0, description="Frequency penalty"
    )
    presence_penalty: Optional[float] = Field(
        None, ge=-2.0, le=2.0, description="Presence penalty"
    )
    stop: Optional[Union[str, list[str]]] = Field(None, description="Stop sequences")
    stream: bool = Field(False, description="Enable streaming response")
    user: Optional[str] = Field(None, description="User ID for tracking")
    timeout: Optional[float] = Field(
        30.0, gt=0, description="Request timeout in seconds"
    )

    @field_validator("stop")
    @classmethod
    def validate_stop(
        cls, v: Optional[Union[str, list[str]]]
    ) -> Optional[Union[str, list[str]]]:
        if isinstance(v, list) and len(v) > 4:
            raise ValueError("Maximum 4 stop sequences allowed")
        return v


class Usage(BaseModel):
    """Token usage information."""

    prompt_tokens: int = Field(..., ge=0, description="Tokens in the prompt")
    completion_tokens: int = Field(..., ge=0, description="Tokens in the completion")
    total_tokens: int = Field(..., ge=0, description="Total tokens used")


class ChatResponse(BaseModel):
    """Response from chat completion."""

    id: str = Field(..., description="Unique response ID")
    model: str = Field(..., description="Model used for completion")
    content: str = Field(..., description="Generated content")
    finish_reason: Optional[str] = Field(None, description="Reason for completion end")
    usage: Optional[Usage] = Field(None, description="Token usage information")
    created: datetime = Field(
        default_factory=datetime.now, description="Response creation time"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @field_serializer('created')
    def serialize_created(self, value: datetime) -> str:
        return value.isoformat()


class StreamingChunk(BaseModel):
    """A chunk of streaming response."""

    id: str = Field(..., description="Unique response ID")
    model: str = Field(..., description="Model used for completion")
    content: str = Field(..., description="Content chunk")
    finish_reason: Optional[str] = Field(None, description="Reason for completion end")
    created: datetime = Field(
        default_factory=datetime.now, description="Chunk creation time"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @field_serializer('created')
    def serialize_created(self, value: datetime) -> str:
        return value.isoformat()


class ProviderConfig(BaseModel):
    """Configuration for a provider."""

    api_key: str = Field(..., description="API key for authentication")
    base_url: Optional[str] = Field(None, description="Base URL for API")
    max_retries: int = Field(3, ge=0, description="Maximum number of retries")
    timeout: float = Field(30.0, gt=0, description="Request timeout in seconds")
    rate_limit: Optional[int] = Field(
        None, gt=0, description="Rate limit (requests per minute)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional configuration"
    )

    model_config = ConfigDict(extra="forbid")
