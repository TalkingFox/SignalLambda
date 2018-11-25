data "aws_iam_policy_document" "lambda" {
  statement {
    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }    
  }
}

data "aws_iam_policy_document" "lambda_access_doc" {
  statement {
    actions = [
      "dynamodb:BatchGetItem",
      "dynamodb:DeleteItem",
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:GetRecords",
      "dynamodb:PutItem",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:UpdateItem",
    ]
    resources = [
      "${aws_dynamodb_table.signal-hotel.arn}"
    ]
  }
}

resource "aws_iam_policy" "lambda_access" {
  name = "lambda_access"
  policy = "${data.aws_iam_policy_document.lambda_access_doc.json}"
}

resource "aws_iam_role_policy_attachment" "lambda_dynamo_policy_attach" {
    role       = "${aws_iam_role.iam_for_lambda.name}"
    policy_arn = "${aws_iam_policy.lambda_access.arn}"
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "signal_iam"
  assume_role_policy = "${data.aws_iam_policy_document.lambda.json}"
}

resource "aws_lambda_function" "signal" {
  filename         = "signal.zip"
  function_name    = "signal"
  runtime          = "python3.6"
  handler          = "main.lambda_handler"
  role             = "${aws_iam_role.iam_for_lambda.arn}"
  source_code_hash = "${base64sha256(file("signal.zip"))}"
}
