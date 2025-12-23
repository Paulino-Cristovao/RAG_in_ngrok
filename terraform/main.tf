terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "app_server" {
  ami           = "ami-0c55b159cbfafe1f0" # Example Amazon Linux 2 AMI (us-east-2) - CHANGE THIS for your region
  instance_type = "t2.micro"

  tags = {
    Name = var.instance_name
  }
}
