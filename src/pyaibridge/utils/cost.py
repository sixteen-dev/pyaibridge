"""Cost calculation utilities."""

from __future__ import annotations

from typing import Dict, Optional

from ..core.base import BaseProvider
from ..core.models import Usage


class CostCalculator:
    """Calculates costs for LLM operations."""

    def __init__(self, provider: BaseProvider) -> None:
        """Initialize cost calculator.

        Args:
            provider: Provider instance
        """
        self.provider = provider

    def calculate_usage_cost(self, usage: Usage, model: str) -> Optional[float]:
        """Calculate cost for token usage.

        Args:
            usage: Token usage information
            model: Model name

        Returns:
            Cost in USD, or None if pricing not available
        """
        try:
            model_info = self.provider.get_model_info(model)
            pricing = model_info.get("pricing")

            if not pricing:
                return None

            prompt_cost = usage.prompt_tokens * pricing.get("prompt_per_token", 0)
            completion_cost = usage.completion_tokens * pricing.get(
                "completion_per_token", 0
            )

            return prompt_cost + completion_cost

        except (ValueError, KeyError):
            return None

    def calculate_text_cost(
        self, text: str, model: str, is_prompt: bool = True
    ) -> Optional[float]:
        """Calculate cost for text based on estimated tokens.

        Args:
            text: Text content
            model: Model name
            is_prompt: Whether text is prompt (True) or completion (False)

        Returns:
            Estimated cost in USD, or None if pricing not available
        """
        try:
            model_info = self.provider.get_model_info(model)
            pricing = model_info.get("pricing")

            if not pricing:
                return None

            estimated_tokens = self.provider.estimate_tokens(text)

            if is_prompt:
                return estimated_tokens * pricing.get("prompt_per_token", 0)
            else:
                return estimated_tokens * pricing.get("completion_per_token", 0)

        except (ValueError, KeyError):
            return None

    def get_model_pricing(self, model: str) -> Optional[Dict[str, float]]:
        """Get pricing information for a model.

        Args:
            model: Model name

        Returns:
            Pricing dictionary or None if not available
        """
        try:
            model_info = self.provider.get_model_info(model)
            return model_info.get("pricing")
        except (ValueError, KeyError):
            return None

    def format_cost(self, cost: float) -> str:
        """Format cost for display.

        Args:
            cost: Cost in USD

        Returns:
            Formatted cost string
        """
        if cost < 0.01:
            return f"${cost:.6f}"
        elif cost < 1.0:
            return f"${cost:.4f}"
        else:
            return f"${cost:.2f}"
