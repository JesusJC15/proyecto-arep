variable "project_name" {
  type    = string
  default = "arep"
}

variable "environment" {
  type    = string
  default = "demo"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.42.0.0/16"
}

variable "public_subnet_cidr" {
  type    = string
  default = "10.42.1.0/24"
}

variable "private_subnet_a_cidr" {
  type    = string
  default = "10.42.10.0/24"
}

variable "private_subnet_b_cidr" {
  type    = string
  default = "10.42.11.0/24"
}

variable "public_subnet_az" {
  type    = string
  default = "us-east-1a"
}

variable "private_subnet_a_az" {
  type    = string
  default = "us-east-1a"
}

variable "private_subnet_b_az" {
  type    = string
  default = "us-east-1b"
}

variable "backend_ingress_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"]
}

variable "backend_container_image" {
  type    = string
  default = "123456789012.dkr.ecr.us-east-1.amazonaws.com/arep-demo-backend:latest"
}

variable "production_database_url_placeholder" {
  type    = string
  default = "postgresql+psycopg://replace-in-secret-manager"
}

variable "production_jwt_secret_placeholder" {
  type    = string
  default = "replace-with-secret-manager"
}

variable "database_name" {
  type    = string
  default = "arep_demo"
}

variable "database_username" {
  type    = string
  default = "arep"
}

variable "database_password" {
  type      = string
  sensitive = true
  default   = "replace-me"
}
