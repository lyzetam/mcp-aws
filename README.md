# mcp-aws

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AWS operations as a Python library, LangChain tools, and MCP server.

## Features

- **19 LangChain tools** for use with LangChain/LangGraph agents
- **16 MCP tools** for use with Claude Code and other MCP clients
- **Modular operations layer** usable as a standalone Python library
- Covers **EC2**, **S3**, **Secrets Manager**, **Lambda**, **CloudWatch**, **STS**, **ECR**, **Route53**, and **CloudFormation**

### MCP Tools

| Category | Tools |
|----------|-------|
| EC2 | `ec2_list_instances`, `ec2_start_instance`, `ec2_stop_instance`, `ec2_describe_instance` |
| S3 | `s3_list_buckets`, `s3_list_objects`, `s3_get_object`, `s3_put_object` |
| Secrets Manager | `secrets_list`, `secrets_get`, `secrets_create` |
| Lambda | `lambda_list_functions`, `lambda_invoke` |
| CloudWatch | `cloudwatch_list_log_groups`, `cloudwatch_get_logs` |
| Status | `aws_status` |

### LangChain Tools

| Category | Tools |
|----------|-------|
| EC2 | `aws_ec2_list`, `aws_ec2_status`, `aws_ec2_start`, `aws_ec2_stop` |
| S3 | `aws_s3_list`, `aws_s3_list_buckets`, `aws_s3_get`, `aws_s3_put` |
| Secrets Manager | `aws_secrets_get`, `aws_secrets_list`, `aws_secrets_create` |
| CloudWatch | `aws_logs_tail` |
| Lambda | `aws_lambda_list`, `aws_lambda_invoke` |
| IAM/STS | `aws_iam_whoami`, `aws_status` |
| ECR | `aws_ecr_list` |
| Route53 | `aws_route53_list` |
| CloudFormation | `aws_cloudformation_list` |

## Installation

```bash
# Core library only (boto3)
pip install .

# With MCP server support
pip install ".[mcp]"

# With LangChain tools
pip install ".[langchain]"

# Everything
pip install ".[all]"
```

## Configuration

All settings are read from environment variables with the `AWS_` prefix, or from a `.env` file.

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key ID | `""` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | `""` |
| `AWS_PROFILE` | AWS profile name | `""` |

## Quick Start

### As a Python library

```python
from mcp_aws.client import AWSClient
from mcp_aws.operations import ec2, s3

client = AWSClient()
instances = ec2.list_instances(client)
buckets = s3.list_buckets(client)
```

### As LangChain tools

```python
from mcp_aws.langchain_tools import TOOLS

# Use with a LangChain agent
agent = create_react_agent(llm, TOOLS)
```

### As an MCP server

```bash
mcp-aws
```

### `.env` example

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

## License

MIT
