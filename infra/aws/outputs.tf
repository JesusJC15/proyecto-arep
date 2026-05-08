output "frontend_bucket_name" {
  value = aws_s3_bucket.frontend.bucket
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "backend_service_name" {
  value = aws_ecs_service.backend.name
}

output "database_endpoint" {
  value = aws_db_instance.postgres.address
}
