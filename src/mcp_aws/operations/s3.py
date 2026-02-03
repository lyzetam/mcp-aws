"""S3 operations."""

from __future__ import annotations

from typing import Any

from ..client import AWSClient


def list_buckets(client: AWSClient) -> list[dict[str, str]]:
    """List all S3 buckets in the account.

    Returns:
        List of dicts with Name and Created.
    """
    s3 = client.get_client("s3")
    response = s3.list_buckets()
    return [
        {"Name": b["Name"], "Created": str(b["CreationDate"])}
        for b in response["Buckets"]
    ]


def list_objects(
    client: AWSClient,
    bucket: str,
    prefix: str | None = None,
    max_keys: int = 100,
) -> list[dict[str, Any]]:
    """List objects in an S3 bucket.

    Returns:
        List of dicts with Key, Size, Modified.
    """
    s3 = client.get_client("s3")
    params: dict[str, Any] = {"Bucket": bucket, "MaxKeys": max_keys}
    if prefix:
        params["Prefix"] = prefix

    response = s3.list_objects_v2(**params)
    return [
        {"Key": obj["Key"], "Size": obj["Size"], "Modified": str(obj["LastModified"])}
        for obj in response.get("Contents", [])
    ]


def get_object(client: AWSClient, bucket: str, key: str) -> str:
    """Get the contents of an S3 object (text files only).

    Returns:
        Content as UTF-8 text.
    """
    s3 = client.get_client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    return response["Body"].read().decode("utf-8")


def put_object(client: AWSClient, bucket: str, key: str, content: str) -> str:
    """Upload text content to an S3 object.

    Returns:
        Success message with S3 URI.
    """
    s3 = client.get_client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=content.encode("utf-8"))
    return f"Successfully uploaded to s3://{bucket}/{key}"
