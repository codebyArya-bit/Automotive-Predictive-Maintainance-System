# AutoMind Infrastructure Variables

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "automind"
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = "AutoMind Team"
}

# Kubernetes Configuration
variable "kubernetes_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.27"
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS worker nodes"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_group_min_size" {
  description = "Minimum number of nodes in the EKS node group"
  type        = number
  default     = 1
}

variable "node_group_max_size" {
  description = "Maximum number of nodes in the EKS node group"
  type        = number
  default     = 10
}

variable "node_group_desired_size" {
  description = "Desired number of nodes in the EKS node group"
  type        = number
  default     = 3
}

# Database Configuration
variable "use_external_db" {
  description = "Whether to use external RDS database instead of in-cluster PostgreSQL"
  type        = bool
  default     = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Initial allocated storage for RDS instance (GB)"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS instance (GB)"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "automind_db"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "automind_user"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
  default     = "change_me_in_production"
}

# Cache Configuration
variable "use_external_cache" {
  description = "Whether to use external ElastiCache instead of in-cluster Redis"
  type        = bool
  default     = true
}

variable "cache_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable monitoring stack (Prometheus, Grafana)"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable centralized logging (ELK stack)"
  type        = bool
  default     = true
}

# SSL/TLS Configuration
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "automind.com"
}

variable "create_route53_zone" {
  description = "Whether to create Route53 hosted zone"
  type        = bool
  default     = false
}

# Backup Configuration
variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

# Security Configuration
variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enable_waf" {
  description = "Enable AWS WAF for additional security"
  type        = bool
  default     = false
}

# Cost Optimization
variable "enable_spot_instances" {
  description = "Enable spot instances for cost optimization"
  type        = bool
  default     = false
}

variable "spot_instance_types" {
  description = "EC2 spot instance types"
  type        = list(string)
  default     = ["t3.medium", "t3.large", "m5.large"]
}

# Auto Scaling Configuration
variable "enable_cluster_autoscaler" {
  description = "Enable cluster autoscaler"
  type        = bool
  default     = true
}

variable "enable_horizontal_pod_autoscaler" {
  description = "Enable horizontal pod autoscaler"
  type        = bool
  default     = true
}

variable "enable_vertical_pod_autoscaler" {
  description = "Enable vertical pod autoscaler"
  type        = bool
  default     = false
}

# Application Configuration
variable "api_image_tag" {
  description = "Docker image tag for the API"
  type        = string
  default     = "latest"
}

variable "api_replicas" {
  description = "Number of API replicas"
  type        = number
  default     = 3
}

variable "worker_replicas" {
  description = "Number of Celery worker replicas"
  type        = number
  default     = 2
}

# Environment-specific overrides
variable "environment_config" {
  description = "Environment-specific configuration overrides"
  type = map(object({
    node_instance_types    = list(string)
    node_group_min_size   = number
    node_group_max_size   = number
    node_group_desired_size = number
    db_instance_class     = string
    cache_node_type       = string
    api_replicas          = number
    worker_replicas       = number
  }))
  default = {
    dev = {
      node_instance_types     = ["t3.small"]
      node_group_min_size    = 1
      node_group_max_size    = 3
      node_group_desired_size = 1
      db_instance_class      = "db.t3.micro"
      cache_node_type        = "cache.t3.micro"
      api_replicas           = 1
      worker_replicas        = 1
    }
    staging = {
      node_instance_types     = ["t3.medium"]
      node_group_min_size    = 2
      node_group_max_size    = 5
      node_group_desired_size = 2
      db_instance_class      = "db.t3.small"
      cache_node_type        = "cache.t3.small"
      api_replicas           = 2
      worker_replicas        = 1
    }
    prod = {
      node_instance_types     = ["t3.large", "m5.large"]
      node_group_min_size    = 3
      node_group_max_size    = 10
      node_group_desired_size = 3
      db_instance_class      = "db.t3.medium"
      cache_node_type        = "cache.t3.medium"
      api_replicas           = 3
      worker_replicas        = 2
    }
  }
}