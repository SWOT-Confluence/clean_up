# Standard imports
import argparse
import datetime
import logging
import os
import pathlib
import shutil

# Third-party imports
import boto3
import botocore


logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S',
                    level=logging.INFO)

class CleanUp:
    """Class to clean up after Confluence workflow execution."""

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

    def __init__(self, prefix):
        """
        Parameters:
        prefix (str): Indicates the AWS environment venue
        """

        self.s3_map = f"{prefix}-map-state"

    def efs(self):
        """Remove all files from the EFS."""

        for efs_dir in self.EFS_DIRS:
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

    def s3(self):
        """Remove all files from S3 Map State bucket."""

        paginator = self.S3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(
            Bucket=self.s3_map
        )
        key_count = list(page_iterator)[0]["KeyCount"]
        if key_count > 0:
            items = { "Objects": [ {"Key": key["Key"] } for page in page_iterator for key in page["Contents"]]}
            self.S3.delete_objects(Bucket=self.s3_map, Delete=items)
            for item in items["Objects"]: logging.info("Deleted s3://%s/%s", self.s3_map, item["Key"])

def create_args():
    """Create and return argparser with arguments."""

    arg_parser = argparse.ArgumentParser(description="Redrive Confluence Step Function failures")
    arg_parser.add_argument("-p",
                            "--prefix",
                            type=str,
                            default="confluence-dev1",
                            help="Prefix that indicates AWS environment venue.")
    return arg_parser

def run_clean_up():
    """Run clean up operations on EFS and Map State S3 bucket."""

    start = datetime.datetime.now()
    arg_parser = create_args()
    args = arg_parser.parse_args()
    prefix = args.prefix
    logging.info("Prefix: %s", prefix)
    clean_up = CleanUp(prefix)
    clean_up.efs()
    clean_up.s3()
    end = datetime.datetime.now()
    logging.info("Elapsed time: %s", end - start)

if __name__ == "__main__":
    run_clean_up()