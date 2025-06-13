# AWS Log Monitor with Slack Notifications

This project demonstrates a secure implementation of a serverless log monitoring solution using AWS CloudWatch and Slack notifications. It follows security best practices and implements proper access controls.

## Security Architecture

The solution implements several security controls:

- **Least Privilege Access**: IAM roles and policies are scoped to minimum required permissions
- **Secure Configuration Management**: Sensitive data (Slack webhook) stored in Parameter Store as SecureString
- **Encryption at Rest**: All sensitive parameters are encrypted
- **Secure Communication**: HTTPS for Slack webhook communication
- **Audit Trail**: CloudWatch Logs for all Lambda executions
- **Resource Isolation**: Specific resource ARNs in IAM policies
- **Secure Secrets Management**: Sensitive values are managed outside of Terraform
- **Dynamic Account Resolution**: AWS account ID is obtained dynamically using aws_caller_identity

## Components

- **AWS Lambda Function**: Implements secure log monitoring with proper error handling
- **CloudWatch Alarm**: Triggers based on error patterns
- **Parameter Store**: Secure storage for configuration
- **IAM Roles**: Following principle of least privilege

## Prerequisites

- AWS CLI with appropriate credentials
- Terraform (tested with 1.5.4)
- Python 3.11
- Slack workspace with webhook capability

## Security Configuration

1. Create `terraform.tfvars` with non-sensitive values:

```hcl
log_group_name    = "your-log-group-name"
log_stream_name   = "your-log-stream-name"
```

2. Set up Parameter Store values securely:

```bash
# Create log group parameter (non-sensitive)
aws ssm put-parameter \
    --name "log-group" \
    --value "your-log-group-name-value" \
    --type String

# create slack webhook parameter (sensitive)
aws ssm put-parameter \
    --name "slack-webhook-url" \
    --value "your-webhook-url-value" \
    --type securestring

# create slack channel parameter (sensitive)
aws ssm put-parameter \
    --name "slack-channel" \
    --value "slack-channel-value" \
    --type securestring
```

Note: Sensitive values should never be stored in Terraform files or state. They should be managed through Parameter Store or a secure secrets management solution.

## Secure Deployment

1. Initialize Terraform:
```bash
terraform init
```

2. Review security changes:
```bash
terraform plan
```

3. Apply with security validation:
```bash
terraform apply
```

## Security Testing

The included test script helps validate the security controls:

1. Install dependencies:
```bash
cd scripts
pip install -r requirements.txt
```

2. Run security tests:
```bash
python generate_test_logs.py \
    --log-group "your-log-group" \
    --log-stream "your-log-stream" \
    --num-logs 10
```

## Security Maintenance

To update security configurations:

1. Parameter Store (preferred method) ex:
```bash
aws ssm put-parameter \
    --name "log-group" \
    --value "your-log-group-name-value" \
    --type String
```

## Security Cleanup

To securely remove resources:
```bash
terraform destroy
```

## Notes

- I tested this in us-east-1, but it should work in other regions
- The error detection is pretty basic right now (just looks for "ERROR" in the logs)
