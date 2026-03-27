# src/services/token_tracker.py
"""
Token Usage Tracker - tracks LLM token usage per project/user

Uses Redis for distributed tracking with monthly aggregation.
"""

import time
import json
from datetime import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class TokenTracker:
    """Track token usage per project with Redis backend."""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self._default_monthly_limit = 1_000_000  # 1M tokens default

    def _get_month_key(self, project_id: str, year: int = None, month: int = None) -> str:
        """Get Redis key for monthly usage."""
        if year is None:
            now = datetime.now()
            year = now.year
            month = now.month
        return f"p9i:usage:{project_id}:{year:04d}-{month:02d}"

    def _get_limit_key(self, project_id: str) -> str:
        """Get Redis key for token limits."""
        return f"p9i:limits:{project_id}"

    async def record_usage(
        self,
        project_id: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        model: str = "unknown",
        cost_usd: float = 0.0
    ) -> Dict:
        """
        Record token usage for a project.

        Args:
            project_id: Project identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: LLM model used
            cost_usd: Cost in USD (calculated from provider rates)

        Returns:
            Updated usage stats
        """
        if not self.redis:
            logger.warning("Redis not available, skipping token tracking")
            return {"error": "Redis not available"}

        now = datetime.now()
        key = self._get_month_key(project_id, now.year, now.month)

        # Get current usage
        current = await self.redis.hgetall(key)
        usage = {
            "input_tokens": int(current.get("input_tokens", 0)),
            "output_tokens": int(current.get("output_tokens", 0)),
            "total_tokens": int(current.get("total_tokens", 0)),
            "requests": int(current.get("requests", 0)),
            "cost_usd": float(current.get("cost_usd", 0)),
        }

        # Update usage
        usage["input_tokens"] += input_tokens
        usage["output_tokens"] += output_tokens
        usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
        usage["requests"] += 1
        usage["cost_usd"] += cost_usd

        # Store in Redis with 35 day TTL (keep 1 month + buffer)
        await self.redis.hset(key, mapping={
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "total_tokens": usage["total_tokens"],
            "requests": usage["requests"],
            "cost_usd": round(usage["cost_usd"], 4),
            "model": model,
            "updated_at": datetime.now().isoformat()
        })
        await self.redis.expire(key, 35 * 24 * 3600)

        logger.info(f"Token usage recorded for {project_id}: {input_tokens} in, {output_tokens} out, ${cost_usd:.4f}")
        return usage

    async def get_usage(self, project_id: str, year: int = None, month: int = None) -> Dict:
        """Get token usage for a project."""
        if not self.redis:
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "requests": 0,
                "cost_usd": 0
            }

        key = self._get_month_key(project_id, year, month)
        current = await self.redis.hgetall(key)

        if not current:
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "requests": 0,
                "cost_usd": 0
            }

        return {
            "input_tokens": int(current.get("input_tokens", 0)),
            "output_tokens": int(current.get("output_tokens", 0)),
            "total_tokens": int(current.get("total_tokens", 0)),
            "requests": int(current.get("requests", 0)),
            "cost_usd": round(float(current.get("cost_usd", 0)), 4),
            "model": current.get("model", "unknown"),
            "updated_at": current.get("updated_at", "")
        }

    async def get_all_usage(self, project_id: str) -> Dict:
        """Get usage for current month and limits."""
        now = datetime.now()

        # Get current month usage
        current = await self.get_usage(project_id, now.year, now.month)

        # Get limits
        limits = await self.get_limits(project_id)

        # Calculate percentages
        if limits["monthly_limit"] > 0:
            current["usage_percent"] = round(
                (current["total_tokens"] / limits["monthly_limit"]) * 100, 1
            )
            current["remaining_tokens"] = max(0, limits["monthly_limit"] - current["total_tokens"])
        else:
            current["usage_percent"] = 0
            current["remaining_tokens"] = -1  # Unlimited

        current["limits"] = limits
        current["month"] = f"{now.year:04d}-{now.month:02d}"

        return current

    async def set_limits(
        self,
        project_id: str,
        monthly_limit: int = 1_000_000,
        alert_percent: int = 80,
        block_percent: int = 100
    ) -> Dict:
        """Set token limits for a project."""
        if not self.redis:
            return {"error": "Redis not available"}

        key = self._get_limit_key(project_id)
        await self.redis.hset(key, mapping={
            "monthly_limit": monthly_limit,
            "alert_percent": alert_percent,
            "block_percent": block_percent,
            "updated_at": datetime.now().isoformat()
        })

        logger.info(f"Token limits set for {project_id}: {monthly_limit} tokens/month")
        return {
            "monthly_limit": monthly_limit,
            "alert_percent": alert_percent,
            "block_percent": block_percent
        }

    async def get_limits(self, project_id: str) -> Dict:
        """Get token limits for a project."""
        if not self.redis:
            return {
                "monthly_limit": self._default_monthly_limit,
                "alert_percent": 80,
                "block_percent": 100
            }

        key = self._get_limit_key(project_id)
        limits = await self.redis.hgetall(key)

        if not limits:
            return {
                "monthly_limit": self._default_monthly_limit,
                "alert_percent": 80,
                "block_percent": 100
            }

        return {
            "monthly_limit": int(limits.get("monthly_limit", self._default_monthly_limit)),
            "alert_percent": int(limits.get("alert_percent", 80)),
            "block_percent": int(limits.get("block_percent", 100))
        }

    async def check_limit(self, project_id: str) -> tuple[bool, str]:
        """
        Check if project is within token limits.

        Returns:
            tuple: (allowed: bool, reason: str)
        """
        usage = await self.get_usage(project_id)
        limits = await self.get_limits(project_id)

        if limits["monthly_limit"] <= 0:
            return True, "unlimited"

        percent = (usage["total_tokens"] / limits["monthly_limit"]) * 100

        if percent >= limits["block_percent"]:
            return False, "limit_exceeded"
        elif percent >= limits["alert_percent"]:
            return True, "warning"

        return True, "ok"


# Global instance
_token_tracker: Optional[TokenTracker] = None


def get_token_tracker(redis_client=None) -> TokenTracker:
    """Get or create token tracker instance."""
    global _token_tracker
    if _token_tracker is None:
        _token_tracker = TokenTracker(redis_client)
    return _token_tracker
