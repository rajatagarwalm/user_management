import boto3
import os
from botocore.exceptions import ClientError
from logger import logger
from datetime import date, datetime

table = boto3.resource("dynamodb").Table(os.environ["DYNAMO_TABLE"])


def _normalize_for_dynamodb(data: dict) -> dict:
    normalized = {}

    for k, v in data.items():
        if isinstance(v, (date, datetime)):
            normalized[k] = v.isoformat()
        else:
            normalized[k] = v

    return normalized


def save_profile(user_id: str, email: str, data: dict):
    try:
        logger.info("Saving profile for user_id=%s", user_id)
        item = {
            "user_id": user_id,
            "email": email,
            **_normalize_for_dynamodb(data)
        }

        table.put_item(Item=item)

    except ClientError as e:
        logger.exception(
            "DynamoDB write failed for user_id=%s | error=%s",
            user_id,
            e.response.get("Error", {})
        )
        raise


def get_profile(user_id: str):
    try:
        logger.info("Fetching profile for user_id=%s", user_id)

        response = table.get_item(Key={"user_id": user_id})
        return response.get("Item", {})

    except ClientError as e:
        logger.exception(
            "DynamoDB read failed for user_id=%s | error=%s",
            user_id,
            e.response.get("Error", {})
        )
        raise


def get_all_profiles(limit: int, last_evaluated_key: dict | None = None):
    try:
        logger.info(
            "Scanning profiles | limit=%s | last_evaluated_key=%s",
            limit,
            last_evaluated_key
        )

        scan_kwargs = {"Limit": limit}

        if last_evaluated_key:
            scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

        response = table.scan(**scan_kwargs)

        return {
            "items": response.get("Items", []),
            "last_evaluated_key": response.get("LastEvaluatedKey")
        }

    except ClientError as e:
        logger.exception(
            "DynamoDB scan failed | error=%s",
            e.response.get("Error", {})
        )
        raise
