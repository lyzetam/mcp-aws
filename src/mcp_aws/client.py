"""AWS client with boto3 session management."""

from __future__ import annotations

import os

import boto3


class AWSClient:
    """Manages boto3 sessions and service clients.

    Reads credentials from environment variables by default:
    - AWS_REGION (default: us-east-1)
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_PROFILE
    """

    def __init__(
        self,
        region: str | None = None,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        profile: str | None = None,
    ) -> None:
        self.region = (region or os.environ.get("AWS_REGION", "us-east-1")).strip()
        self.access_key_id = (
            access_key_id or os.environ.get("AWS_ACCESS_KEY_ID", "")
        ).strip()
        self.secret_access_key = (
            secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY", "")
        ).strip()
        self.profile = (profile or os.environ.get("AWS_PROFILE", "")).strip()

    def session(self) -> boto3.Session:
        """Create a boto3 session with configured credentials."""
        if self.access_key_id and self.secret_access_key:
            return boto3.Session(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region,
            )
        if self.profile:
            return boto3.Session(profile_name=self.profile, region_name=self.region)
        return boto3.Session(region_name=self.region)

    def get_client(self, service: str):
        """Get a boto3 client for the specified AWS service."""
        return self.session().client(service)
