output "ag_base_url" {
    value = "${aws_api_gateway_deployment.signal_deploy.invoke_url}"
}

output "cf_base_url" {
    value = "${aws_cloudfront_distribution.ag_distribution.domain_name}"
}