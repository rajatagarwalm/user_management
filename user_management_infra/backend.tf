terraform {
  backend "s3" {
    bucket         = "rajat-terraform-state-dev"
    key            = "user-management/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "terraform-locks"
  }
}
