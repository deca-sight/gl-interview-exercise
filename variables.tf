variable "log_group_name" {
  description = "Name of the log group to monitor (non-sensitive value)"
  type        = string
}

variable "log_stream_name" {
  description = "Name of the log stream"
  type        = string
}

variable "region" {
  description = "AWS region where resources will be deployed"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# Note: Sensitive values like slack_webhook_url should be managed through Parameter Store
# and not passed through Terraform variables. This ensures sensitive data is not stored
# in the Terraform state or repository.
