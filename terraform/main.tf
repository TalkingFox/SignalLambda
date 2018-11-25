provider "aws" {
  region = "us-east-2"
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "signal_iam"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_function" "signal" {
  filename      = "signal.zip"
  function_name = "signal"
  runtime       = "python3.6"
  handler       = "main.lambda_handler"
  role          = "${aws_iam_role.iam_for_lambda.arn}"
  source_code_hash = "${base64sha256(file("signal.zip"))}"
}
