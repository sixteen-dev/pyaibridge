"""Metrics collection utilities."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


class MetricsCollector:
    """Collects and tracks metrics for LLM operations."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.metrics: Dict[str, Any] = defaultdict(lambda: defaultdict(int))
        self.timing_metrics: Dict[str, list[float]] = defaultdict(list)
        self.start_times: Dict[str, float] = {}

    def increment(self, metric: str, provider: str, value: int = 1) -> None:
        """Increment a counter metric.

        Args:
            metric: Metric name
            provider: Provider name
            value: Value to increment by
        """
        self.metrics[provider][metric] += value
        logger.debug(
            "Metric incremented", metric=metric, provider=provider, value=value
        )

    def start_timer(self, operation: str, provider: str) -> None:
        """Start timing an operation.

        Args:
            operation: Operation name
            provider: Provider name
        """
        key = f"{provider}:{operation}"
        self.start_times[key] = time.time()

    def end_timer(self, operation: str, provider: str) -> float:
        """End timing an operation and record duration.

        Args:
            operation: Operation name
            provider: Provider name

        Returns:
            Duration in seconds
        """
        key = f"{provider}:{operation}"
        start_time = self.start_times.pop(key, None)

        if start_time is None:
            logger.warning("Timer not started", operation=operation, provider=provider)
            return 0.0

        duration = time.time() - start_time
        self.timing_metrics[key].append(duration)

        logger.debug(
            "Timer ended", operation=operation, provider=provider, duration=duration
        )
        return duration

    def record_tokens(
        self, provider: str, prompt_tokens: int, completion_tokens: int
    ) -> None:
        """Record token usage.

        Args:
            provider: Provider name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
        """
        self.metrics[provider]["prompt_tokens"] += prompt_tokens
        self.metrics[provider]["completion_tokens"] += completion_tokens
        self.metrics[provider]["total_tokens"] += prompt_tokens + completion_tokens

    def record_cost(self, provider: str, cost: float) -> None:
        """Record cost for an operation.

        Args:
            provider: Provider name
            cost: Cost in USD
        """
        self.metrics[provider]["total_cost"] += cost
        self.metrics[provider]["cost_count"] += 1

    def get_metrics(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get collected metrics.

        Args:
            provider: Optional provider to filter by

        Returns:
            Metrics dictionary
        """
        if provider:
            return dict(self.metrics.get(provider, {}))
        return dict(self.metrics)

    def get_timing_stats(self, operation: str, provider: str) -> Dict[str, float]:
        """Get timing statistics for an operation.

        Args:
            operation: Operation name
            provider: Provider name

        Returns:
            Timing statistics
        """
        key = f"{provider}:{operation}"
        times = self.timing_metrics.get(key, [])

        if not times:
            return {}

        return {
            "count": len(times),
            "min": min(times),
            "max": max(times),
            "avg": sum(times) / len(times),
            "total": sum(times),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()
        self.timing_metrics.clear()
        self.start_times.clear()
        logger.info("Metrics reset")

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics.

        Returns:
            Summary dictionary
        """
        summary = {}

        for provider, metrics in self.metrics.items():
            provider_summary = dict(metrics)

            # Add timing summaries
            timing_summary = {}
            for key, times in self.timing_metrics.items():
                if key.startswith(f"{provider}:"):
                    operation = key.split(":", 1)[1]
                    timing_summary[operation] = {
                        "count": len(times),
                        "avg_duration": sum(times) / len(times) if times else 0,
                        "total_duration": sum(times),
                    }

            if timing_summary:
                provider_summary["timing"] = timing_summary

            summary[provider] = provider_summary

        return summary


# Global metrics collector instance
metrics = MetricsCollector()
