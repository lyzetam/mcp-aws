"""Pydantic Settings configuration for mcp-aws."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AWS configuration from environment variables or .env file.

    All fields map to AWS_<FIELD_NAME> environment variables.
    """

    region: str = Field(default="us-east-1", description="AWS region")
    access_key_id: str = Field(default="", description="AWS access key ID")
    secret_access_key: str = Field(default="", description="AWS secret access key")
    profile: str = Field(default="", description="AWS profile name")

    model_config = SettingsConfigDict(
        env_prefix="AWS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Get configuration from environment variables or .env file."""
    return Settings()
