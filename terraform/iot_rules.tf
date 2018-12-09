resource "aws_iot_topic_rule" "disconnect" {
  name        = "user_disconnected"
  description = "user_disconnected"
  enabled     = true
  sql         = "select * from '$aws/events/presence/disconnected/#'"
  sql_version = "2015-10-08"

  lambda {
    function_arn = "${aws_lambda_function.room_deleter.arn}"
  }
}

resource "aws_lambda_permission" "iot_lambda" {
  statement_id = "AllowExecutionFromIot"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.room_deleter.function_name}"
  principal = "iot.amazonaws.com"
  source_arn = "${aws_iot_topic_rule.disconnect.arn}"
}

