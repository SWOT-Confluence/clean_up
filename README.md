# clean up

Cleans up after Confluence workflow by:
1) Removing all files and sub-directories in the EFS.
2) Deleting all data from the Map State S3 bucket.

**Note only downloads gauge and sword data if it does not exist.**

This is a docker container meant to be run as an AWS Batch job after the output
module or manually.

## installation

Build a Docker image: `docker build -t clean_up .`

## execution

`aws batch submit-job --profile <named_profile> --cli-input-json file://cleanup.json`

where `<named_profile>` is the name of the profile defined in your AWS credential file and `cleanup.json` is a file with the following contents:

```json
{
    "jobName": "confluence-dev1-clean-up-0",
    "jobQueue": "confluence-dev1-clean-up",
    "propagateTags": true,
    "tags": {
        "job": "confluence-dev1-clean-up-0",
        "application": "confluence",
        "Name": "confluence-dev1-clean-up-0"
    },
    "jobDefinition": "confluence-dev1-clean-up",
    "containerOverrides": {
        "command": [
            "-p",
            "confluence-dev1"
        ]
    }
}
```

where `-p` indiates the prefix for the AWS environment Confluence is exeucting in.

### docker

AWS credentials will need to be passed as environment variables to the container so that `clean_up` may access AWS infrastructure to generate JSON files.

```bash
# Credentials
export aws_key=XXXXXXXXXXXXXX
export aws_secret=XXXXXXXXXXXXXXXXXXXXXXXXXX

# Docker run command
docker run --rm --name clean_up -e AWS_ACCESS_KEY_ID=$aws_key -e AWS_SECRET_ACCESS_KEY=$aws_secret -e AWS_DEFAULT_REGION=us-west-2 clean_up:latest
```

### cli



## deployment

There is a script to deploy the Docker container image and Terraform AWS infrastructure found in the `deploy` directory.

Script to deploy Terraform and Docker image AWS infrastructure

REQUIRES:

- jq (<https://jqlang.github.io/jq/>)
- docker (<https://docs.docker.com/desktop/>) > version Docker 1.5
- AWS CLI (<https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html>)
- Terraform (<https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli>)

Command line arguments:

[1] registry: Registry URI
[2] repository: Name of repository to create
[3] prefix: Prefix to use for AWS resources associated with environment deploying to
[4] s3_state_bucket: Name of the S3 bucket to store Terraform state in (no need for s3:// prefix)
[5] profile: Name of profile used to authenticate AWS CLI commands

Example usage: ``./deploy.sh "account-id.dkr.ecr.region.amazonaws.com" "container-image-name" "prefix-for-environment" "s3-state-bucket-name" "confluence-named-profile"`

Note: Run the script from the deploy directory.
