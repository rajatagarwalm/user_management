output "api_base_url" {
  value = "${aws_api_gateway_deployment.deploy.invoke_url}${aws_api_gateway_stage.prod.stage_name}"
}


output "admin_group_name" {
  value = aws_cognito_user_group.admin.name
}

output "user_pool_id" {
  value = aws_cognito_user_pool.this.id
}

output "user_pool_client_id" {
  value = aws_cognito_user_pool_client.this.id
}

output "identity_pool_id" {
  value = aws_cognito_identity_pool.this.id
}

output "s3_bucket" {
  value = aws_s3_bucket.profile_images.bucket
}

