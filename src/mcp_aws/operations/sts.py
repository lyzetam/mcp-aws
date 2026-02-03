"""STS operations."""

from __future__ import annotations

from typing import Any

from ..client import AWSClient


def get_caller_identity(client: AWSClient) -> dict[str, Any]:
    """Get the current AWS caller identity.

    Returns:
        Dict with region, account, arn, and user_id.
    """
    sts = client.get_client("sts")
    identity = sts.get_caller_identity()
    return {
        "region": client.region,
        "account": identity["Account"],
        "arn": identity["Arn"],
        "user_id": identity["UserId"],
    }
