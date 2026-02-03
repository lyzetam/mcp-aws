"""Tests for AWS operations using moto mocks."""

import json
import zipfile
from io import BytesIO

import boto3
import pytest
from moto import mock_aws

from mcp_aws.client import AWSClient
from mcp_aws.operations import (
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


@pytest.fixture
def client():
    """AWSClient with test credentials."""
    return AWSClient(
        region="us-east-1",
        access_key_id="testing",
        secret_access_key="testing",
    )


# =============================================================================
# EC2
# =============================================================================


@mock_aws
def test_ec2_list_instances_empty(client):
    result = ec2.list_instances(client)
    assert result == []


@mock_aws
def test_ec2_list_instances(client):
    ec2_client = client.get_client("ec2")
    ec2_client.run_instances(
        ImageId="ami-12345678",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": "test-instance"}],
        }],
    )
    result = ec2.list_instances(client)
    assert len(result) == 1
    assert result[0]["Name"] == "test-instance"
    assert result[0]["Type"] == "t2.micro"
    assert result[0]["State"] == "running"


@mock_aws
def test_ec2_describe_instance(client):
    ec2_client = client.get_client("ec2")
    resp = ec2_client.run_instances(ImageId="ami-12345678", MinCount=1, MaxCount=1, InstanceType="t2.micro")
    instance_id = resp["Instances"][0]["InstanceId"]

    result = ec2.describe_instance(client, instance_id)
    assert result["InstanceId"] == instance_id
    assert result["InstanceType"] == "t2.micro"


@mock_aws
def test_ec2_stop_start_instance(client):
    ec2_client = client.get_client("ec2")
    resp = ec2_client.run_instances(ImageId="ami-12345678", MinCount=1, MaxCount=1, InstanceType="t2.micro")
    instance_id = resp["Instances"][0]["InstanceId"]

    stop_msg = ec2.stop_instance(client, instance_id)
    assert instance_id in stop_msg

    start_msg = ec2.start_instance(client, instance_id)
    assert instance_id in start_msg


# =============================================================================
# S3
# =============================================================================


@mock_aws
def test_s3_list_buckets(client):
    s3_client = client.get_client("s3")
    s3_client.create_bucket(Bucket="test-bucket")
    result = s3.list_buckets(client)
    assert len(result) == 1
    assert result[0]["Name"] == "test-bucket"


@mock_aws
def test_s3_list_objects(client):
    s3_client = client.get_client("s3")
    s3_client.create_bucket(Bucket="test-bucket")
    s3_client.put_object(Bucket="test-bucket", Key="hello.txt", Body=b"hello")

    result = s3.list_objects(client, "test-bucket")
    assert len(result) == 1
    assert result[0]["Key"] == "hello.txt"


@mock_aws
def test_s3_get_put_object(client):
    s3_client = client.get_client("s3")
    s3_client.create_bucket(Bucket="test-bucket")

    msg = s3.put_object(client, "test-bucket", "test.txt", "hello world")
    assert "s3://test-bucket/test.txt" in msg

    content = s3.get_object(client, "test-bucket", "test.txt")
    assert content == "hello world"


# =============================================================================
# Secrets Manager
# =============================================================================


@mock_aws
def test_secrets_create_and_get(client):
    result = secrets.create_secret(client, "test/secret", '{"key": "value"}', description="test")
    assert result["status"] == "created"
    assert result["name"] == "test/secret"

    value = secrets.get_secret(client, "test/secret")
    assert json.loads(value) == {"key": "value"}


@mock_aws
def test_secrets_list(client):
    secrets.create_secret(client, "test/secret1", "val1")
    secrets.create_secret(client, "test/secret2", "val2")

    result = secrets.list_secrets(client)
    names = [s["Name"] for s in result]
    assert "test/secret1" in names
    assert "test/secret2" in names


# =============================================================================
# Lambda
# =============================================================================


def _make_lambda_zip():
    """Create a minimal Lambda deployment zip."""
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("lambda_function.py", "def handler(event, context): return 'ok'")
    buf.seek(0)
    return buf.read()


@mock_aws
def test_lambda_list_functions(client):
    lam = client.get_client("lambda")
    # Create IAM role for Lambda
    iam = client.get_client("iam")
    iam.create_role(
        RoleName="test-role",
        AssumeRolePolicyDocument="{}",
        Path="/",
    )
    lam.create_function(
        FunctionName="test-func",
        Runtime="python3.12",
        Role="arn:aws:iam::123456789012:role/test-role",
        Handler="lambda_function.handler",
        Code={"ZipFile": _make_lambda_zip()},
    )

    result = lambda_.list_functions(client)
    assert len(result) == 1
    assert result[0]["Name"] == "test-func"
    assert result[0]["Runtime"] == "python3.12"


@mock_aws
def test_lambda_invoke(client):
    lam = client.get_client("lambda")
    iam = client.get_client("iam")
    iam.create_role(RoleName="test-role", AssumeRolePolicyDocument="{}", Path="/")
    lam.create_function(
        FunctionName="test-func",
        Runtime="python3.12",
        Role="arn:aws:iam::123456789012:role/test-role",
        Handler="lambda_function.handler",
        Code={"ZipFile": _make_lambda_zip()},
    )

    result = lambda_.invoke(client, "test-func")
    assert isinstance(result, str)


# =============================================================================
# CloudWatch
# =============================================================================


@mock_aws
def test_cloudwatch_list_log_groups(client):
    logs = client.get_client("logs")
    logs.create_log_group(logGroupName="/aws/test")

    result = cloudwatch.list_log_groups(client)
    assert len(result) >= 1
    names = [g["name"] for g in result]
    assert "/aws/test" in names


@mock_aws
def test_cloudwatch_list_log_groups_with_prefix(client):
    logs = client.get_client("logs")
    logs.create_log_group(logGroupName="/aws/test")
    logs.create_log_group(logGroupName="/other/group")

    result = cloudwatch.list_log_groups(client, prefix="/aws")
    names = [g["name"] for g in result]
    assert "/aws/test" in names
    assert "/other/group" not in names


@mock_aws
def test_cloudwatch_get_logs_empty(client):
    logs = client.get_client("logs")
    logs.create_log_group(logGroupName="/aws/test")

    result = cloudwatch.get_logs(client, "/aws/test")
    assert result == []


# =============================================================================
# STS
# =============================================================================


@mock_aws
def test_sts_get_caller_identity(client):
    result = sts.get_caller_identity(client)
    assert "account" in result
    assert "arn" in result
    assert result["region"] == "us-east-1"


# =============================================================================
# ECR
# =============================================================================


@mock_aws
def test_ecr_list_repositories(client):
    ecr_client = client.get_client("ecr")
    ecr_client.create_repository(repositoryName="test-repo")

    result = ecr.list_repositories(client)
    assert len(result) == 1
    assert result[0]["name"] == "test-repo"


# =============================================================================
# Route53
# =============================================================================


@mock_aws
def test_route53_list_hosted_zones(client):
    r53 = client.get_client("route53")
    r53.create_hosted_zone(Name="example.com", CallerReference="ref1")

    result = route53.list_hosted_zones(client)
    assert len(result) >= 1
    assert result[0]["name"] == "example.com."


# =============================================================================
# CloudFormation
# =============================================================================


@mock_aws
def test_cloudformation_list_stacks(client):
    cf = client.get_client("cloudformation")
    cf.create_stack(
        StackName="test-stack",
        TemplateBody=json.dumps({
            "AWSTemplateFormatVersion": "2010-09-09",
            "Resources": {},
        }),
    )

    result = cloudformation.list_stacks(client)
    names = [s["name"] for s in result]
    assert "test-stack" in names
