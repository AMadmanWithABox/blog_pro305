import boto3
from boto3.dynamodb.conditions import Key
from os import getenv
from uuid import uuid4
import json

region_name = getenv('APP_REGION')
blog_post_table = boto3.resource('dynamodb', region_name=region_name).Table('BlogPost2024')


def lambda_handler(event, context):
    http_method = event["httpMethod"]

    if "body" in event and event["body"] is not None:
        event = json.loads(event["body"])

    if http_method == "POST":
        return create_post(event, context)
    elif http_method == "GET":
        return get_post(event, context)
    elif http_method == "PUT":
        return update_post(event, context)
    elif http_method == "DELETE":
        return delete_post(event, context)
    pass


def create_post(event, context):
    pass


def get_post(event, context):
    pass


def update_post(event, context):
    pass


def delete_post(event, context):
    pass


def response(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body),
        "isBase64Encoded": False
    }