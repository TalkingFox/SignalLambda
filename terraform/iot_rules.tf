resource "aws_iot_topic_rule" "disconnect" {
    name = "user_disconnected"
    description = "user_disconnected"
    enabled = true
    sql = "select * from '$aws/events/presence/disconnected/#'"
    sql_version = "2015-10-08"
    lambda {
        function_arn = "${aws_lambda_function.room_deleter.arn}"
    }
}