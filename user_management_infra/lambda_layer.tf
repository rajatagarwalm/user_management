resource "aws_lambda_layer_version" "python_deps" {
  layer_name = "${var.project_name}-python-deps"

  filename   = "lambda_layer.zip"
  compatible_runtimes = ["python3.10"]

  source_code_hash = filebase64sha256("lambda_layer.zip")
}
