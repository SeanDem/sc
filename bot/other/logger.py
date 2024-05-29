import boto3
import watchtower
import logging


def setup_logger():
    boto3_client = boto3.client("logs", region_name="us-east-2")
    cw_handler = watchtower.CloudWatchLogHandler(
        log_group_name="sc-bot", boto3_client=boto3_client
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(cw_handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    return logger


LOGGER = setup_logger()
