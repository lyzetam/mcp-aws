"""Secrets Manager operations."""

from __future__ import annotations

from typing import Any

from ..client import AWSClient


def list_secrets(client: AWSClient, max_results: int = 500) -> list[dict[str, str]]:
    """List secrets in AWS Secrets Manager.

    Paginates past the AWS API's hard cap of 100 results per call by following
    NextToken until ``max_results`` is reached or there are no more pages.

    Returns:
        List of dicts with Name and ARN (up to ``max_results``).
    """
    sm = client.get_client("secretsmanager")
    out: list[dict[str, str]] = []
    next_token: str | None = None
    while len(out) < max_results:
        kwargs: dict[str, Any] = {"MaxResults": min(100, max_results - len(out))}
        if next_token:
            kwargs["NextToken"] = next_token
        response = sm.list_secrets(**kwargs)
        out.extend(
            {"Name": s["Name"], "ARN": s["ARN"]}
            for s in response.get("SecretList", [])
        )
        next_token = response.get("NextToken")
        if not next_token:
            break
    return out[:max_results]


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
