variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "instance_name" {
  description = "Value of the Name tag for the EC2 instance"
  type        = string
  default     = "LangChainChatAgent"
}
