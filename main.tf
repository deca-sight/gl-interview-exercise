# Get the current AWS account ID
data "aws_caller_identity" "current" {}

module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.0"

  function_name = "log-error-monitor"
  description   = "Monitors logs and sends error notifications to Slack"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  source_path   = "lambda"

  attach_policy_statements = true
  policy_statements = [
    {
      effect = "Allow"
      actions = [
        "logs:FilterLogEvents",
        "logs:GetLogEvents",
        "logs:DescribeLogStreams"
      ]
      resources = ["arn:aws:logs:${var.region}:${data.aws_caller_identity.current.account_id}:log-group:${var.log_group_name}:*"]
    },
    {
      effect = "Allow"
      actions = [
        "ssm:GetParameter",
        "ssm:GetParameters"
      ]
      resources = [
        "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/log-group",
        "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/slack-channel",
        "arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter/slack-webhook-url"
      ]
    }
  ]

  cloudwatch_logs_retention_in_days = 7
}

# Note: Parameter Store values should be created manually or through a secure CI/CD process
# Example AWS CLI commands to create the parameters:
# aws ssm put-parameter --name "/log-monitor/log-group-name" --value "your-log-group" --type String
# aws ssm put-parameter --name "/log-monitor/slack-webhook-url" --value "your-webhook-url" --type SecureString

resource "aws_cloudwatch_log_metric_filter" "error_filter" {
  name           = "ErrorMetricFilter"
  log_group_name = var.log_group_name
  pattern        = "\"ERROR\""

  metric_transformation {
    name      = "ErrorCount"
    namespace = "LogMonitoring"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "error_alarm" {
  alarm_name          = "LogErrorAlarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.error_filter.metric_transformation[0].name
  namespace           = aws_cloudwatch_log_metric_filter.error_filter.metric_transformation[0].namespace
  period              = 60
  statistic           = "Sum"
  threshold           = 1

  alarm_actions = [module.lambda_function.lambda_function_arn]
  treat_missing_data = "notBreaching"
}

resource "aws_lambda_permission" "allow_cloudwatch_alarm" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function.lambda_function_name
  principal     = "lambda.alarms.cloudwatch.amazonaws.com"
  source_arn    = aws_cloudwatch_metric_alarm.error_alarm.arn
}

