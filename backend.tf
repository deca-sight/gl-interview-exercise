//terraform {
//  backend "s3" {
//    bucket         = "infra-org-tfstate"      # reemplazalo con tu bucket
//    key            = "org/terraform.tfstate"
//    region         = "us-east-1"
//    dynamodb_table = "infra-org-tflock"       # tabla para locking
//    encrypt        = true
//  }
//}

resource "aws_s3_bucket" "tfstate" {
  bucket = "gl-interview-exercise-state"
}

resource "aws_dynamodb_table" "tflock" {
  name         = "gl-interview-tflock"
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

