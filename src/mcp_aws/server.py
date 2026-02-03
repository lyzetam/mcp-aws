"""AWS MCP Server — thin wrappers delegating to operations."""

from __future__ import annotations

import json
from typing import Optional

from botocore.exceptions import ClientError, NoCredentialsError
from fastmcp import FastMCP

from .client import AWSClient
from .operations import (
    cloudwatch,
    ec2,
    lambda_,
    s3,
    secrets,
    sts,
)

mcp = FastMCP("aws-mcp")

_client = AWSClient()


def _error(e: ClientError) -> str:
    return f"AWS Error: {e.response['Error']['Message']}"


# =============================================================================
# EC2
# =============================================================================


@mcp.tool
def ec2_list_instances(filters: Optional[list] = None) -> str:
    """List EC2 instances with their status, type, and IPs.

    Args:
        filters: Optional filters (e.g., [{'Name': 'instance-state-name', 'Values': ['running']}])
    """
    try:
        return json.dumps(ec2.list_instances(_client, filters=filters), indent=2, default=str)
    except ClientError as e:
        return _error(e)
    except NoCredentialsError:
        return "Error: No AWS credentials configured"


@mcp.tool
def ec2_start_instance(instance_id: str) -> str:
    """Start an EC2 instance.

    Args:
        instance_id: EC2 instance ID (e.g., i-1234567890abcdef0)
    """
    try:
        return ec2.start_instance(_client, instance_id)
    except ClientError as e:
        return _error(e)


@mcp.tool
def ec2_stop_instance(instance_id: str) -> str:
    """Stop an EC2 instance.

    Args:
        instance_id: EC2 instance ID
    """
    try:
        return ec2.stop_instance(_client, instance_id)
    except ClientError as e:
        return _error(e)


@mcp.tool
def ec2_describe_instance(instance_id: str) -> str:
    """Get detailed information about a specific EC2 instance.

    Args:
        instance_id: EC2 instance ID
    """
    try:
        return json.dumps(ec2.describe_instance(_client, instance_id), indent=2, default=str)
    except ClientError as e:
        return _error(e)


# =============================================================================
# S3
# =============================================================================


@mcp.tool
def s3_list_buckets() -> str:
    """List all S3 buckets in the account."""
    try:
        return json.dumps(s3.list_buckets(_client), indent=2, default=str)
    except ClientError as e:
        return _error(e)


@mcp.tool
def s3_list_objects(bucket: str, prefix: Optional[str] = None, max_keys: int = 100) -> str:
    """List objects in an S3 bucket.

    Args:
        bucket: S3 bucket name
        prefix: Optional prefix to filter objects
        max_keys: Maximum number of keys to return (default 100)
    """
    try:
        return json.dumps(
            s3.list_objects(_client, bucket, prefix=prefix, max_keys=max_keys),
            indent=2,
            default=str,
        )
    except ClientError as e:
        return _error(e)


@mcp.tool
def s3_get_object(bucket: str, key: str) -> str:
    """Get the contents of an S3 object (text files only).

    Args:
        bucket: S3 bucket name
        key: Object key (path)
    """
    try:
        return s3.get_object(_client, bucket, key)
    except ClientError as e:
        return _error(e)


@mcp.tool
def s3_put_object(bucket: str, key: str, content: str) -> str:
    """Upload content to an S3 object.

    Args:
        bucket: S3 bucket name
        key: Object key (path)
        content: Content to upload
    """
    try:
        return s3.put_object(_client, bucket, key, content)
    except ClientError as e:
        return _error(e)


# =============================================================================
# Secrets Manager
# =============================================================================


@mcp.tool
def secrets_list(max_results: int = 100) -> str:
    """List secrets in AWS Secrets Manager.

    Args:
        max_results: Maximum number of results (default 100)
    """
    try:
        return json.dumps(secrets.list_secrets(_client, max_results=max_results), indent=2)
    except ClientError as e:
        return _error(e)


@mcp.tool
def secrets_get(secret_id: str) -> str:
    """Get a secret value from AWS Secrets Manager.

    Args:
        secret_id: Secret name or ARN
    """
    try:
        return secrets.get_secret(_client, secret_id)
    except ClientError as e:
        return _error(e)


@mcp.tool
def secrets_create(name: str, secret_value: str, description: Optional[str] = None) -> str:
    """Create a new secret in AWS Secrets Manager.

    Args:
        name: Name of the secret (e.g., 'prod/myapp/api-key')
        secret_value: The secret value (string or JSON string)
        description: Optional description for the secret
    """
    try:
        result = secrets.create_secret(_client, name, secret_value, description=description)
        return json.dumps(result, indent=2)
    except ClientError as e:
        return _error(e)


# =============================================================================
# Lambda
# =============================================================================


@mcp.tool
def lambda_list_functions() -> str:
    """List Lambda functions."""
    try:
        return json.dumps(lambda_.list_functions(_client), indent=2, default=str)
    except ClientError as e:
        return _error(e)


@mcp.tool
def lambda_invoke(function_name: str, payload: Optional[dict] = None) -> str:
    """Invoke a Lambda function.

    Args:
        function_name: Lambda function name
        payload: JSON payload to send to the function
    """
    try:
        return lambda_.invoke(_client, function_name, payload=payload)
    except ClientError as e:
        return _error(e)


# =============================================================================
# CloudWatch
# =============================================================================


@mcp.tool
def cloudwatch_list_log_groups(prefix: Optional[str] = None) -> str:
    """List CloudWatch log groups.

    Args:
        prefix: Optional prefix to filter log groups
    """
    try:
        return json.dumps(cloudwatch.list_log_groups(_client, prefix=prefix), indent=2)
    except ClientError as e:
        return _error(e)


@mcp.tool
def cloudwatch_get_logs(
    log_group: str,
    log_stream: Optional[str] = None,
    limit: int = 50,
) -> str:
    """Get recent log events from a CloudWatch log group.

    Args:
        log_group: CloudWatch log group name
        log_stream: Optional log stream name
        limit: Maximum number of events (default 50)
    """
    try:
        return json.dumps(
            cloudwatch.get_logs(_client, log_group, log_stream=log_stream, limit=limit),
            indent=2,
            default=str,
        )
    except ClientError as e:
        return _error(e)


# =============================================================================
# Status
# =============================================================================


@mcp.tool
def aws_status() -> str:
    """Check AWS connection status and configured region."""
    try:
        identity = sts.get_caller_identity(_client)
        return json.dumps({"status": "connected", **identity}, indent=2)
    except NoCredentialsError:
        return "No AWS credentials configured"
    except ClientError as e:
        return f"Connection error: {e.response['Error']['Message']}"


def main():
    """Entry point for MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
