# Staging Environment Configuration
environment = "staging"
project_name = "automind"
owner = "platform-team"

# AWS Configuration
aws_region = "us-west-2"

# Kubernetes Configuration
kubernetes_version = "1.28"
node_group_min_size = 2
node_group_max_size = 6
node_group_desired_size = 3
node_group_instance_types = ["t3.large"]

# Database Configuration
use_external_rds = true
db_instance_class = "db.t3.small"
db_allocated_storage = 50
db_storage_encrypted = true
db_name = "automind_staging"
db_username = "automind_user"
# db_password is set via environment variable TF_VAR_db_password

# Cache Configuration
use_external_elasticache = true
cache_node_type = "cache.t3.small"

# Domain and SSL
domain_name = "staging.automind.com"
create_route53_zone = true

# Security
allowed_cidr_blocks = ["10.0.0.0/8", "172.16.0.0/12"]
enable_waf = true

# Monitoring and Logging
enable_monitoring = true
enable_logging = true

# Backup Configuration
backup_retention_period = 14

# Cost Optimization
enable_spot_instances = true

# Auto Scaling
enable_cluster_autoscaler = true
enable_horizontal_pod_autoscaler = true
enable_vertical_pod_autoscaler = true

# Application Configuration
api_image_tag = "main"
api_replicas = 3
worker_replicas = 2

# Tags
tags = {
  Environment = "staging"
  Project = "automind"
  Owner = "platform-team"
  CostCenter = "engineering"
  Backup = "daily"
  Compliance = "required"
}