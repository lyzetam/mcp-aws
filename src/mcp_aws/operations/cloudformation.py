"""CloudFormation operations."""

from __future__ import annotations

from typing import Any

from ..client import AWSClient


def list_stacks(
    client: AWSClient,
    status_filter: list[str] | None = None,
) -> list[dict[str, Any]]:
    """List CloudFormation stacks.

    Args:
        client: AWSClient instance.
        status_filter: Optional list of stack status values to filter by
            (e.g., ['CREATE_COMPLETE', 'UPDATE_COMPLETE']).

    Returns:
        List of dicts with name, status, and created.
    """
    cf = client.get_client("cloudformation")
    params: dict[str, Any] = {}
    if status_filter:
        params["StackStatusFilter"] = status_filter

    response = cf.list_stacks(**params)
    return [
        {
            "name": s["StackName"],
            "status": s["StackStatus"],
            "created": str(s["CreationTime"]),
        }
        for s in response.get("StackSummaries", [])
    ]
