# Job Definition
resource "aws_batch_job_definition" "generate_batch_jd_clean_up" {
  name = "${var.prefix}-clean-up"
  type = "container"
  platform_capabilities = ["FARGATE"]
  propagate_tags = true
  tags = { "job_definition": "${var.prefix}-clean-up" }

  container_properties = jsonencode({
    image = "${local.account_id}.dkr.ecr.us-west-2.amazonaws.com/${var.prefix}-clean-up:${var.image_tag}"
    executionRoleArn = var.iam_execution_role_arn
    jobRoleArn = var.iam_job_role_arn
    fargatePlatformConfiguration = {
      platformVersion = "LATEST"
    }
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group = aws_cloudwatch_log_group.cw_log_group.name
      }
    }
    resourceRequirements = [{
      type = "MEMORY"
      value = "512"
    }, {
      type = "VCPU",
      value = "0.25"
    }]
    mountPoints = [{
      sourceVolume = "input",
      containerPath = "/mnt/input"
      readOnly = false
    }, {
      sourceVolume = "flpe"
      containerPath = "/mnt/flpe"
      readOnly = false
    }, {
      sourceVolume = "moi"
      containerPath = "/mnt/moi"
      readOnly = false
    }, {
      sourceVolume = "diagnostics"
      containerPath = "/mnt/diagnostics"
      readOnly = false
    }, {
      sourceVolume = "offline"
      containerPath = "/mnt/offline"
      readOnly = false
    }, {
      sourceVolume = "validation"
      containerPath = "/mnt/validation"
      readOnly = false
    }, {
      sourceVolume = "output"
      containerPath = "/mnt/output"
      readOnly = false
    }, {
      sourceVolume = "logs"
      containerPath = "/mnt/logs"
      readOnly = false
    }]
    volumes = [{
      name = "input"
      efsVolumeConfiguration = {
        fileSystemId = var.efs_file_system_ids["input"]
        rootDirectory = "/"
      }
    }, {
      name = "flpe"
      efsVolumeConfiguration = {
        fileSystemId = var.efs_file_system_ids["flpe"]
        rootDirectory = "/"
      }
    }, {
      name = "moi"
      efsVolumeConfiguration = {
        fileSystemId = var.efs_file_system_ids["moi"]
        rootDirectory = "/"
      }
    }, {
      name = "diagnostics"
      efsVolumeConfiguration = {
        fileSystemId = var.efs_file_system_ids["diagnostics"]
        rootDirectory = "/"
      }
    }, {
      name = "offline"
      efsVolumeConfiguration = {
        fileSystemId = var.efs_file_system_ids["offline"]
        rootDirectory = "/"
      }
    }, {
      name = "validation"
      efsVolumeConfiguration = {
        fileSystemId = var.efs_file_system_ids["validation"]
        rootDirectory = "/"
      }
    }, {
      name = "output"
      efsVolumeConfiguration = {
        fileSystemId = var.efs_file_system_ids["output"]
        rootDirectory = "/"
      }
    }, {
      name = "logs"
      efsVolumeConfiguration = {
        fileSystemId = var.efs_file_system_ids["logs"]
        rootDirectory = "/"
      }
    }]
  })
}

# Log group
resource "aws_cloudwatch_log_group" "cw_log_group" {
  name = "/aws/batch/job/${var.prefix}-clean-up/"
}
