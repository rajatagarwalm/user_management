resource "aws_lambda_function" "api" {
  function_name = "${var.project_name}-api"
  runtime       = "python3.10"
  handler       = "lambda_function.lambda_handler"
  role          = aws_iam_role.lambda_role.arn

  filename         = "lambda.zip"
  source_code_hash = filebase64sha256("lambda.zip")

  layers = [
    aws_lambda_layer_version.python_deps.arn
  ]

  timeout      = 30
  memory_size = 512

  environment {
    variables = {
      DYNAMO_TABLE          = aws_dynamodb_table.users.name
      COGNITO_USER_POOL_ID  = aws_cognito_user_pool.this.id
      COGNITO_CLIENT_ID    = aws_cognito_user_pool_client.this.id
    }
  }
}
