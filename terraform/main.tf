# Data sources
data "aws_caller_identity" "current" {}

data "aws_cloudwatch_log_group" "cw_log_group" {
  name = "/aws/batch/job/${var.prefix}-clean-up/"
}

data "aws_efs_file_system" "input" {
  creation_token = "${var.prefix}-input"
}

data "aws_efs_file_system" "flpe" {
  creation_token = "${var.prefix}-flpe"
}

data "aws_efs_file_system" "moi" {
  creation_token = "${var.prefix}-moi"
}

data "aws_efs_file_system" "diagnostics" {
  creation_token = "${var.prefix}-diagnostics"
}

data "aws_efs_file_system" "offline" {
  creation_token = "${var.prefix}-offline"
}

data "aws_efs_file_system" "validation" {
  creation_token = "${var.prefix}-validation"
}

data "aws_efs_file_system" "output" {
  creation_token = "${var.prefix}-output"
}

data "aws_efs_file_system" "logs" {
  creation_token = "${var.prefix}-logs"
}

data "aws_iam_role" "job" {
  name = "${var.prefix}-batch-job-role"
}

data "aws_iam_role" "exec" {
  name = "${var.prefix}-ecs-exe-task-role"
}

# Local variables
locals {
  account_id = data.aws_caller_identity.current.account_id
  default_tags = length(var.default_tags) == 0 ? {
    application : var.app_name,
    environment : lower(var.environment),
    version : var.app_version
  } : var.default_tags
}

module "confluence-clean-up" {
  source            = "./modules/clean"
  app_name          = var.app_name
  app_version       = var.app_version
  aws_region        = var.aws_region
  environment       = var.environment
  prefix            = var.prefix
  iam_execution_role_arn = data.aws_iam_role.exec.arn
  iam_job_role_arn = data.aws_iam_role.job.arn
  efs_file_system_ids = {
    input = data.aws_efs_file_system.aws_efs_input.arn
    flpe = data.aws_efs_file_system.flpe.arn
    moi = data.aws_efs_file_system.moi.arn
    diagnostics = data.aws_efs_file_system.diagnostics.arn
    offline = data.aws_efs_file_system.offline.arn
    logs = data.aws_efs_file_system.logs.arn
  }
}
