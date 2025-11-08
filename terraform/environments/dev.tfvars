# Development Environment Configuration
environment = "dev"
project_name = "automind"
owner = "development-team"

# AWS Configuration
aws_region = "us-west-2"

# Kubernetes Configuration
kubernetes_version = "1.28"
node_group_min_size = 1
node_group_max_size = 3
node_group_desired_size = 2
node_group_instance_types = ["t3.medium"]

# Database Configuration
use_external_rds = true
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
db_storage_encrypted = true
db_name = "automind_dev"
db_username = "automind_user"
# db_password is set via environment variable TF_VAR_db_password

# Cache Configuration
use_external_elasticache = true
cache_node_type = "cache.t3.micro"

# Domain and SSL
domain_name = "dev.automind.local"
create_route53_zone = false

# Security
allowed_cidr_blocks = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
enable_waf = false

# Monitoring and Logging
enable_monitoring = true
enable_logging = true

# Backup Configuration
backup_retention_period = 7

# Cost Optimization
enable_spot_instances = true

# Auto Scaling
enable_cluster_autoscaler = true
enable_horizontal_pod_autoscaler = true
enable_vertical_pod_autoscaler = false

# Application Configuration
api_image_tag = "develop"
api_replicas = 2
worker_replicas = 1

# Tags
tags = {
  Environment = "development"
  Project = "automind"
  Owner = "development-team"
  CostCenter = "engineering"
  Backup = "daily"
}