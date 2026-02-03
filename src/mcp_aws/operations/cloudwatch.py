"""CloudWatch Logs operations."""

from __future__ import annotations

from typing import Any

from ..client import AWSClient


def list_log_groups(
    client: AWSClient,
    prefix: str | None = None,
) -> list[dict[str, Any]]:
    """List CloudWatch log groups.

    Returns:
        List of dicts with name and storedBytes.
    """
    logs = client.get_client("logs")
    params: dict[str, Any] = {}
    if prefix:
        params["logGroupNamePrefix"] = prefix
    response = logs.describe_log_groups(**params)
    return [
        {"name": g["logGroupName"], "storedBytes": g.get("storedBytes", 0)}
        for g in response.get("logGroups", [])
    ]


def get_logs(
    client: AWSClient,
    log_group: str,
    log_stream: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Get recent log events from a CloudWatch log group.

    If log_stream is not specified, fetches from the most recent stream.

    Returns:
        List of dicts with timestamp and message.
    """
    logs = client.get_client("logs")

    if log_stream:
        response = logs.get_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            limit=limit,
        )
        events = response.get("events", [])
    else:
        streams = logs.describe_log_streams(
            logGroupName=log_group,
            orderBy="LastEventTime",
            descending=True,
            limit=1,
        )
        if streams.get("logStreams"):
            stream_name = streams["logStreams"][0]["logStreamName"]
            response = logs.get_log_events(
                logGroupName=log_group,
                logStreamName=stream_name,
                limit=limit,
            )
            events = response.get("events", [])
        else:
            events = []

    return [{"timestamp": e["timestamp"], "message": e["message"]} for e in events]
