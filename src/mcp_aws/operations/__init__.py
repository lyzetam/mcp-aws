"""AWS operations — pure boto3 business logic with no framework dependencies."""

from .cloudformation import list_stacks
from .cloudwatch import get_logs, list_log_groups
from .ec2 import describe_instance, list_instances, start_instance, stop_instance
from .ecr import list_repositories
from .lambda_ import invoke, list_functions
from .route53 import list_hosted_zones
from .s3 import get_object, list_buckets, list_objects, put_object
from .secrets import create_secret, get_secret, list_secrets
from .sts import get_caller_identity

__all__ = [
    # EC2
    "list_instances",
    "start_instance",
    "stop_instance",
    "describe_instance",
    # S3
    "list_buckets",
    "list_objects",
    "get_object",
    "put_object",
    # Secrets Manager
    "list_secrets",
    "get_secret",
    "create_secret",
    # Lambda
    "list_functions",
    "invoke",
    # CloudWatch
    "list_log_groups",
    "get_logs",
    # STS
    "get_caller_identity",
    # ECR
    "list_repositories",
    # Route53
    "list_hosted_zones",
    # CloudFormation
    "list_stacks",
]
