"""ECR operations."""

from __future__ import annotations

from typing import Any

from ..client import AWSClient


def list_repositories(client: AWSClient) -> list[dict[str, Any]]:
    """List ECR repositories.

    Returns:
        List of dicts with name, uri, and created.
    """
    ecr = client.get_client("ecr")
    response = ecr.describe_repositories()
    return [
        {
            "name": r["repositoryName"],
            "uri": r["repositoryUri"],
            "created": str(r["createdAt"]),
        }
        for r in response.get("repositories", [])
    ]
