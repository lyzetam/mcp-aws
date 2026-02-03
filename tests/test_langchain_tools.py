"""Tests for LangChain tool interfaces."""

from langchain_core.tools import BaseTool

from mcp_aws.langchain_tools import TOOLS


def test_tools_count():
    """Verify TOOLS list has the expected number of tools."""
    assert len(TOOLS) == 19


def test_all_tools_are_base_tool():
    """Every entry in TOOLS must be a LangChain BaseTool instance."""
    for t in TOOLS:
        assert isinstance(t, BaseTool), f"{t} is not a BaseTool"


def test_tool_names_follow_convention():
    """All tool names should start with aws_."""
    for t in TOOLS:
        assert t.name.startswith("aws_"), f"Tool {t.name} does not follow aws_ naming convention"


def test_tool_names_are_unique():
    """No duplicate tool names."""
    names = [t.name for t in TOOLS]
    assert len(names) == len(set(names)), f"Duplicate tool names: {names}"


def test_expected_tools_present():
    """Check key tools are in the TOOLS list."""
    names = {t.name for t in TOOLS}
    expected = {
        "aws_ec2_list",
        "aws_ec2_status",
        "aws_ec2_start",
        "aws_ec2_stop",
        "aws_s3_list",
        "aws_s3_list_buckets",
        "aws_s3_get",
        "aws_s3_put",
        "aws_secrets_get",
        "aws_secrets_list",
        "aws_secrets_create",
        "aws_logs_tail",
        "aws_lambda_list",
        "aws_lambda_invoke",
        "aws_iam_whoami",
        "aws_status",
        "aws_ecr_list",
        "aws_route53_list",
        "aws_cloudformation_list",
    }
    assert expected == names


def test_all_tools_have_descriptions():
    """Every tool should have a non-empty description."""
    for t in TOOLS:
        assert t.description, f"Tool {t.name} has no description"
