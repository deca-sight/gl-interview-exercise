resource "aws_cloudwatch_log_group" "my_log_group" {
  name              = var.log_group_name
  retention_in_days = 7
}

resource "aws_cloudwatch_log_stream" "my_log_stream" {
  name           = var.log_stream_name
  log_group_name = aws_cloudwatch_log_group.my_log_group.name
}

resource "aws_iam_role" "log_writer" {
  name = "log-writer-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"  
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "log_writer_policy" {
  name = "log-writer-policy"
  role = aws_iam_role.log_writer.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "logs:PutLogEvents",
        "logs:CreateLogStream",
        "logs:DescribeLogStreams"
      ],
      Resource = [
        "${aws_cloudwatch_log_group.my_log_group.arn}:*"
      ]
    }]
  })
}

