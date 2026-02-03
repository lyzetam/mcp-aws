"""LangChain @tool wrappers for AWS operations.

Usage:
    from mcp_aws.langchain_tools import TOOLS

    # Or import individual tools:
    from mcp_aws.langchain_tools import aws_s3_list, aws_secrets_get
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .client import AWSClient
from .operations import (
    cloudformation,
    cloudwatch,
    ec2,
    ecr,
    lambda_,
    route53,
    s3,
    secrets,
    sts,
)


@lru_cache
def _get_client() -> AWSClient:
    """Singleton AWSClient configured from environment."""
    return AWSClient()


# =============================================================================
# EC2
# =============================================================================


class EC2ListInput(BaseModel):
    region: str | None = Field(default=None, description="AWS region")
    state: str | None = Field(default=None, description="Filter by state: running, stopped, etc.")


@tool(args_schema=EC2ListInput)
def aws_ec2_list(region: str | None = None, state: str | None = None) -> str:
    """List EC2 instances with ID, type, state, and name."""
    client = _get_client()
    filters = []
    if state:
        filters.append({"Name": "instance-state-name", "Values": [state]})
    instances = ec2.list_instances(client, filters=filters or None)
    return json.dumps(instances, indent=2, default=str)


class EC2StatusInput(BaseModel):
    instance_id: str = Field(description="EC2 instance ID")


@tool(args_schema=EC2StatusInput)
def aws_ec2_status(instance_id: str) -> str:
    """Get detailed information about a specific EC2 instance."""
    return json.dumps(ec2.describe_instance(_get_client(), instance_id), indent=2, default=str)


class EC2StartInput(BaseModel):
    instance_id: str = Field(description="EC2 instance ID (e.g., i-1234567890abcdef0)")


@tool(args_schema=EC2StartInput)
def aws_ec2_start(instance_id: str) -> str:
    """Start an EC2 instance."""
    return ec2.start_instance(_get_client(), instance_id)


class EC2StopInput(BaseModel):
    instance_id: str = Field(description="EC2 instance ID")


@tool(args_schema=EC2StopInput)
def aws_ec2_stop(instance_id: str) -> str:
    """Stop an EC2 instance."""
    return ec2.stop_instance(_get_client(), instance_id)


# =============================================================================
# S3
# =============================================================================


class S3ListInput(BaseModel):
    bucket: str = Field(description="S3 bucket name")
    prefix: str = Field(default="", description="Key prefix to filter objects")
    max_items: int = Field(default=100, description="Maximum items to return")


@tool(args_schema=S3ListInput)
def aws_s3_list(bucket: str, prefix: str = "", max_items: int = 100) -> str:
    """List objects in an S3 bucket."""
    objects = s3.list_objects(_get_client(), bucket, prefix=prefix or None, max_keys=max_items)
    return json.dumps(objects, indent=2, default=str)


@tool
def aws_s3_list_buckets() -> str:
    """List all S3 buckets in the account."""
    return json.dumps(s3.list_buckets(_get_client()), indent=2, default=str)


class S3GetInput(BaseModel):
    bucket: str = Field(description="S3 bucket name")
    key: str = Field(description="Object key (path)")


@tool(args_schema=S3GetInput)
def aws_s3_get(bucket: str, key: str) -> str:
    """Read a text object from S3."""
    return s3.get_object(_get_client(), bucket, key)


class S3PutInput(BaseModel):
    bucket: str = Field(description="S3 bucket name")
    key: str = Field(description="Object key (destination path)")
    content: str = Field(description="Content to upload")


@tool(args_schema=S3PutInput)
def aws_s3_put(bucket: str, key: str, content: str) -> str:
    """Upload text content to S3."""
    return s3.put_object(_get_client(), bucket, key, content)


# =============================================================================
# Secrets Manager
# =============================================================================


class SecretsGetInput(BaseModel):
    secret_name: str = Field(description="Secret name or ARN")


@tool(args_schema=SecretsGetInput)
def aws_secrets_get(secret_name: str) -> str:
    """Get a secret from AWS Secrets Manager.

    Returns the secret value. If JSON, returns it pretty-printed.
    """
    value = secrets.get_secret(_get_client(), secret_name)
    try:
        return json.dumps(json.loads(value), indent=2)
    except (json.JSONDecodeError, TypeError):
        return value


class SecretsListInput(BaseModel):
    filter_name: str | None = Field(default=None, description="Filter by name prefix")
    max_results: int = Field(default=50, description="Maximum results")


@tool(args_schema=SecretsListInput)
def aws_secrets_list(filter_name: str | None = None, max_results: int = 50) -> str:
    """List secrets in AWS Secrets Manager."""
    result = secrets.list_secrets(_get_client(), max_results=max_results)
    if filter_name:
        result = [s for s in result if s["Name"].startswith(filter_name)]
    return json.dumps(result, indent=2)


class SecretsCreateInput(BaseModel):
    name: str = Field(description="Secret name")
    value: str = Field(description="Secret value (string or JSON)")
    description: str = Field(default="", description="Description")


@tool(args_schema=SecretsCreateInput)
def aws_secrets_create(name: str, value: str, description: str = "") -> str:
    """Create a new secret in AWS Secrets Manager."""
    result = secrets.create_secret(
        _get_client(), name, value, description=description or None
    )
    return json.dumps(result, indent=2)


# =============================================================================
# CloudWatch Logs
# =============================================================================


class LogsTailInput(BaseModel):
    log_group: str = Field(description="CloudWatch log group name")
    log_stream: Optional[str] = Field(default=None, description="Specific log stream name")
    limit: int = Field(default=50, description="Maximum events to return")


@tool(args_schema=LogsTailInput)
def aws_logs_tail(
    log_group: str,
    log_stream: Optional[str] = None,
    limit: int = 50,
) -> str:
    """Get recent CloudWatch log events."""
    events = cloudwatch.get_logs(
        _get_client(), log_group, log_stream=log_stream, limit=limit
    )
    return json.dumps(events, indent=2, default=str)


# =============================================================================
# Lambda
# =============================================================================


class LambdaListInput(BaseModel):
    region: str | None = Field(default=None, description="AWS region")


@tool(args_schema=LambdaListInput)
def aws_lambda_list(region: str | None = None) -> str:
    """List Lambda functions."""
    return json.dumps(lambda_.list_functions(_get_client()), indent=2, default=str)


class LambdaInvokeInput(BaseModel):
    function_name: str = Field(description="Lambda function name or ARN")
    payload: str = Field(default="{}", description="JSON payload to pass to the function")


@tool(args_schema=LambdaInvokeInput)
def aws_lambda_invoke(function_name: str, payload: str = "{}") -> str:
    """Invoke a Lambda function."""
    payload_dict = json.loads(payload) if payload else {}
    return lambda_.invoke(_get_client(), function_name, payload=payload_dict)


# =============================================================================
# IAM / STS
# =============================================================================


@tool
def aws_iam_whoami() -> str:
    """Get the current AWS caller identity (who am I)."""
    return json.dumps(sts.get_caller_identity(_get_client()), indent=2)


@tool
def aws_status() -> str:
    """Check AWS connection status, region, account, and ARN."""
    try:
        identity = sts.get_caller_identity(_get_client())
        return json.dumps({"status": "connected", **identity}, indent=2)
    except Exception as e:
        return f"Connection error: {e}"


# =============================================================================
# ECR
# =============================================================================


@tool
def aws_ecr_list() -> str:
    """List ECR repositories."""
    return json.dumps(ecr.list_repositories(_get_client()), indent=2, default=str)


# =============================================================================
# Route53
# =============================================================================


@tool
def aws_route53_list() -> str:
    """List Route53 hosted zones."""
    return json.dumps(route53.list_hosted_zones(_get_client()), indent=2, default=str)


# =============================================================================
# CloudFormation
# =============================================================================


class CloudFormationListInput(BaseModel):
    status: str | None = Field(
        default=None,
        description="Filter by status (e.g. CREATE_COMPLETE, UPDATE_COMPLETE)",
    )


@tool(args_schema=CloudFormationListInput)
def aws_cloudformation_list(status: str | None = None) -> str:
    """List CloudFormation stacks."""
    status_filter = [status] if status else None
    return json.dumps(
        cloudformation.list_stacks(_get_client(), status_filter=status_filter),
        indent=2,
        default=str,
    )


# =============================================================================
# Tool exports
# =============================================================================

TOOLS = [
    # EC2
    aws_ec2_list,
    aws_ec2_status,
    aws_ec2_start,
    aws_ec2_stop,
    # S3
    aws_s3_list,
    aws_s3_list_buckets,
    aws_s3_get,
    aws_s3_put,
    # Secrets Manager
    aws_secrets_get,
    aws_secrets_list,
    aws_secrets_create,
    # CloudWatch
    aws_logs_tail,
    # Lambda
    aws_lambda_list,
    aws_lambda_invoke,
    # IAM/STS
    aws_iam_whoami,
    aws_status,
    # ECR
    aws_ecr_list,
    # Route53
    aws_route53_list,
    # CloudFormation
    aws_cloudformation_list,
]
