resource "aws_api_gateway_rest_api" "signalApi" {
  name = "Signal"
  description = "Api Gateway for the signal server"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = "${aws_api_gateway_rest_api.signalApi.id}"
  parent_id = "${aws_api_gateway_rest_api.signalApi.root_resource_id}"
  path_part = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id = "${aws_api_gateway_rest_api.signalApi.id}"
  resource_id = "${aws_api_gateway_resource.proxy.id}"
  http_method = "ANY"
  authorization = "NONE"  
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = "${aws_api_gateway_rest_api.signalApi.id}"
  resource_id = "${aws_api_gateway_method.proxy.resource_id}"
  http_method = "${aws_api_gateway_method.proxy.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.signal.invoke_arn}"
}

resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id = "${aws_api_gateway_rest_api.signalApi.id}"
  resource_id = "${aws_api_gateway_rest_api.signalApi.root_resource_id}"
  http_method = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = "${aws_api_gateway_rest_api.signalApi.id}"
  resource_id = "${aws_api_gateway_method.proxy_root.resource_id}"
  http_method = "${aws_api_gateway_method.proxy_root.http_method}"

  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = "${aws_lambda_function.signal.invoke_arn}"
}

resource "aws_api_gateway_deployment" "signal_deploy" {
  depends_on = [
    "aws_api_gateway_integration.lambda",
    "aws_api_gateway_integration.lambda_root",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.signalApi.id}"
  stage_name  = "deploy"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowExecutionFromApiGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.signal.function_name}"
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.signalApi.execution_arn}/*/*/*"
}


resource "aws_cloudfront_distribution" "ag_distribution" {
  enabled = true

  origin {
    domain_name = "${replace("${aws_api_gateway_deployment.signal_deploy.invoke_url}","/(deploy)|(https://)|(/)/","")}"
    origin_id = "ag_deploy_invoke_url"
    origin_path = "/deploy"
    custom_origin_config {
      http_port = 80
      https_port = 443
      origin_protocol_policy = "match-viewer"
      origin_ssl_protocols = ["SSLv3","TLSv1","TLSv1.1","TLSv1.2"]
    }
  }

  default_cache_behavior {
    viewer_protocol_policy = "allow-all"
    allowed_methods = ["GET","HEAD","OPTIONS","POST","DELETE","PUT","PATCH"]
    cached_methods = ["GET","HEAD"]
    target_origin_id = "ag_deploy_invoke_url"

    
    forwarded_values {
      query_string = true
      cookies {
        forward = "none"
      }
    }    
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  depends_on = ["aws_api_gateway_deployment.signal_deploy"]
}