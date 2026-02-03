"""Lambda operations."""

from __future__ import annotations

import json
from typing import Any

from ..client import AWSClient


def list_functions(client: AWSClient) -> list[dict[str, Any]]:
    """List Lambda functions.

    Returns:
        List of dicts with Name, Runtime, Memory, Timeout.
    """
    lam = client.get_client("lambda")
    response = lam.list_functions()
    return [
        {
            "Name": f["FunctionName"],
            "Runtime": f.get("Runtime", "N/A"),
            "Memory": f["MemorySize"],
            "Timeout": f["Timeout"],
        }
        for f in response.get("Functions", [])
    ]


def invoke(
    client: AWSClient,
    function_name: str,
    payload: dict[str, Any] | None = None,
) -> str:
    """Invoke a Lambda function.

    Returns:
        Lambda function response as string.
    """
    lam = client.get_client("lambda")
    response = lam.invoke(
        FunctionName=function_name,
        Payload=json.dumps(payload or {}),
    )
    return response["Payload"].read().decode("utf-8")
