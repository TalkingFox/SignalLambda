output "base_url" {
    value = "${aws_api_gateway_deployment.signal_deploy.invoke_url}"
}