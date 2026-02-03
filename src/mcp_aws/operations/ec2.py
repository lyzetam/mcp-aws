"""EC2 operations."""

from __future__ import annotations

from typing import Any

from ..client import AWSClient


def list_instances(client: AWSClient, filters: list[dict] | None = None) -> list[dict[str, Any]]:
    """List EC2 instances with their status, type, and IPs.

    Args:
        client: AWSClient instance.
        filters: Optional EC2 filters (e.g., [{'Name': 'instance-state-name', 'Values': ['running']}]).

    Returns:
        List of instance dicts with InstanceId, Name, State, Type, PrivateIp, PublicIp.
    """
    ec2 = client.get_client("ec2")
    response = ec2.describe_instances(Filters=filters or [])

    instances = []
    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            name_tag = next(
                (t["Value"] for t in instance.get("Tags", []) if t["Key"] == "Name"),
                "N/A",
            )
            instances.append({
                "InstanceId": instance["InstanceId"],
                "Name": name_tag,
                "State": instance["State"]["Name"],
                "Type": instance["InstanceType"],
                "PrivateIp": instance.get("PrivateIpAddress", "N/A"),
                "PublicIp": instance.get("PublicIpAddress", "N/A"),
            })
    return instances


def start_instance(client: AWSClient, instance_id: str) -> str:
    """Start an EC2 instance.

    Returns:
        Status message with current state.
    """
    ec2 = client.get_client("ec2")
    response = ec2.start_instances(InstanceIds=[instance_id])
    state = response["StartingInstances"][0]["CurrentState"]["Name"]
    return f"Instance {instance_id} is now {state}"


def stop_instance(client: AWSClient, instance_id: str) -> str:
    """Stop an EC2 instance.

    Returns:
        Status message with current state.
    """
    ec2 = client.get_client("ec2")
    response = ec2.stop_instances(InstanceIds=[instance_id])
    state = response["StoppingInstances"][0]["CurrentState"]["Name"]
    return f"Instance {instance_id} is now {state}"


def describe_instance(client: AWSClient, instance_id: str) -> dict[str, Any]:
    """Get detailed information about a specific EC2 instance.

    Returns:
        Full instance details dict.
    """
    ec2 = client.get_client("ec2")
    response = ec2.describe_instances(InstanceIds=[instance_id])
    return response["Reservations"][0]["Instances"][0]
