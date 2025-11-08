# Production Environment Configuration
environment = "prod"
project_name = "automind"
owner = "platform-team"

# AWS Configuration
aws_region = "us-west-2"

# Kubernetes Configuration
kubernetes_version = "1.28"
node_group_min_size = 3
node_group_max_size = 10
node_group_desired_size = 5
node_group_instance_types = ["m5.large", "m5.xlarge"]

# Database Configuration
use_external_rds = true
db_instance_class = "db.r5.large"
db_allocated_storage = 200
db_storage_encrypted = true
db_name = "automind_prod"
db_username = "automind_user"
# db_password is set via environment variable TF_VAR_db_password

# Cache Configuration
use_external_elasticache = true
cache_node_type = "cache.r5.large"

# Domain and SSL
domain_name = "automind.com"
create_route53_zone = true

# Security
allowed_cidr_blocks = ["0.0.0.0/0"]  # Will be restricted by WAF and security groups
enable_waf = true

# Monitoring and Logging
enable_monitoring = true
enable_logging = true

# Backup Configuration
backup_retention_period = 30

# Cost Optimization
enable_spot_instances = false  # Use on-demand for production stability

# Auto Scaling
enable_cluster_autoscaler = true
enable_horizontal_pod_autoscaler = true
enable_vertical_pod_autoscaler = true

# Application Configuration
api_image_tag = "latest"
api_replicas = 5
worker_replicas = 3

# Tags
tags = {
  Environment = "production"
  Project = "automind"
  Owner = "platform-team"
  CostCenter = "operations"
  Backup = "daily"
  Compliance = "required"
  BusinessCritical = "true"
  DataClassification = "confidential"
}