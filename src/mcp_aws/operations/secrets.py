"""Secrets Manager operations."""

from __future__ import annotations

from typing import Any

from ..client import AWSClient


def list_secrets(client: AWSClient, max_results: int = 100) -> list[dict[str, str]]:
    """List secrets in AWS Secrets Manager.

    Returns:
        List of dicts with Name and ARN.
    """
    sm = client.get_client("secretsmanager")
    response = sm.list_secrets(MaxResults=max_results)
    return [
        {"Name": s["Name"], "ARN": s["ARN"]}
        for s in response.get("SecretList", [])
    ]


def get_secret(client: AWSClient, secret_id: str) -> str:
    """Get a secret value from AWS Secrets Manager.

    Returns:
        The secret value string.
    """
    sm = client.get_client("secretsmanager")
    response = sm.get_secret_value(SecretId=secret_id)
    return response.get("SecretString", response.get("SecretBinary", ""))


def create_secret(
    client: AWSClient,
    name: str,
    secret_value: str,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a new secret in AWS Secrets Manager.

    Returns:
        Dict with status, name, and arn.
    """
    sm = client.get_client("secretsmanager")
    params: dict[str, Any] = {"Name": name, "SecretString": secret_value}
    if description:
        params["Description"] = description

    response = sm.create_secret(**params)
    return {
        "status": "created",
        "name": response["Name"],
        "arn": response["ARN"],
    }
