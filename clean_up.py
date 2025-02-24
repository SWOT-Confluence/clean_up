# Standard imports
import argparse
import datetime
import logging
import os
import pathlib
import shutil
import tempfile

# Third-party imports
import boto3
import botocore


logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S',
                    level=logging.INFO)


COPY_FILES = [
    "continent-setfinder.json",
    "prediagnostics_config.R",
    "reaches_of_interest.json"
]
EFS_DIRS = [
    pathlib.Path("/mnt/input"),
    pathlib.Path("/mnt/flpe"),
    pathlib.Path("/mnt/moi"),
    pathlib.Path("/mnt/diagnostics"),
    pathlib.Path("/mnt/offline"),
    pathlib.Path("/mnt/validation"),
    pathlib.Path("/mnt/output"),
    pathlib.Path("/mnt/logs")
]
S3 = boto3.client("s3")


def delete_efs():
    """Remove all files from the EFS."""

    for efs_dir in EFS_DIRS:
        try:
            with os.scandir(efs_dir) as entries:
                for entry in entries:
                    if entry.is_file():
                        os.unlink(entry.path)
                    else:
                        shutil.rmtree(entry.path)
                    logging.info("Removed %s.", entry.path)
        except OSError as e:
            logging.error(e)
            logging.info("Could not delete files in %s.", efs_dir)

def copy_s3(config_bucket, json_bucket, bucket_key):
    """Copy config files over to JSON bucket to preserve run data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = pathlib.Path(temp_dir)
        for s3_file in COPY_FILES:
            try:
                S3.download_file(
                    config_bucket,
                    s3_file,
                    data_dir.joinpath(s3_file)
                )

                S3.upload_file(
                    data_dir.joinpath(s3_file),
                    json_bucket,
                    f"{bucket_key}/{s3_file}",
                    ExtraArgs={"ServerSideEncryption": "AES256"}
                )
                logging.info("Copied s3://%s/%s/%s.", json_bucket, bucket_key, s3_file)

            except botocore.exceptions.ClientError as e:
                if "404" in str(e):
                    logging.info("Does not exist s3://%s/%s/%s.", json_bucket, bucket_key, s3_file)
                else:
                    logging.error("Error encountered: %s.", str(e))

def create_args():
    """Create and return argparser with arguments."""

    arg_parser = argparse.ArgumentParser(description="Redrive Confluence Step Function failures")
    arg_parser.add_argument("-d",
                            "--delete",
                            help="Indicate EFS files should be deleted.",
                            action="store_true")
    arg_parser.add_argument("-c",
                            "--configbucket",
                            type=str,
                            help="Name of config S3 bucket to copy JSON files from.")
    arg_parser.add_argument("-j",
                            "--jsonbucket",
                            type=str,
                            help="Name of S3 bucket to copy JSON files to.")
    arg_parser.add_argument("-k",
                            "--bucketkey",
                            type=str,
                            help="Name of prefix to upload JSON files to.")
    return arg_parser

def run_clean_up():
    """Run clean up operations on EFS and Map State S3 bucket."""

    start = datetime.datetime.now()
    arg_parser = create_args()
    args = arg_parser.parse_args()

    delete = args.delete
    config_bucket = args.configbucket
    json_bucket = args.jsonbucket
    bucket_key = args.bucketkey

    logging.info("Delete: %s", delete)
    logging.info("Config S3 bucket: %s", config_bucket)
    logging.info("JSON S3 bucket: %s", json_bucket)
    logging.info("S3 bucket key: %s", bucket_key)

    if delete:
        delete_efs()

    copy_s3(config_bucket, json_bucket, bucket_key)

    end = datetime.datetime.now()
    logging.info("Elapsed time: %s", end - start)

if __name__ == "__main__":
    run_clean_up()