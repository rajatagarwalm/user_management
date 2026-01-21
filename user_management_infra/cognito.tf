resource "aws_cognito_user_pool" "this" {
  name = "${var.project_name}-${var.environment}-user-pool"

  auto_verified_attributes = ["email"]

  schema {
    name     = "email"
    required = true
    attribute_data_type = "String"
  }
}

resource "aws_cognito_user_pool_client" "this" {
  name         = "${var.project_name}-client"
  user_pool_id = aws_cognito_user_pool.this.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]
}

resource "aws_cognito_identity_pool" "this" {
  identity_pool_name               = "${var.project_name}-${var.environment}-identity-pool"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id     = aws_cognito_user_pool_client.this.id
    provider_name = aws_cognito_user_pool.this.endpoint
  }
}

resource "aws_cognito_identity_pool_roles_attachment" "this" {
  identity_pool_id = aws_cognito_identity_pool.this.id

  roles = {
    authenticated = aws_iam_role.cognito_authenticated.arn
  }
}

resource "aws_cognito_user_group" "admin" {
  name         = "admin"
  user_pool_id = aws_cognito_user_pool.this.id
  description  = "Admin users with elevated access"
}

