"""Route53 operations."""

from __future__ import annotations

from typing import Any

from ..client import AWSClient


def list_hosted_zones(client: AWSClient) -> list[dict[str, Any]]:
    """List Route53 hosted zones.

    Returns:
        List of dicts with name, id, and record_count.
    """
    r53 = client.get_client("route53")
    response = r53.list_hosted_zones()
    return [
        {
            "name": z["Name"],
            "id": z["Id"],
            "record_count": z["ResourceRecordSetCount"],
        }
        for z in response.get("HostedZones", [])
    ]
