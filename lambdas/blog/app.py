import boto3
from boto3.dynamodb.conditions import Key
from os import getenv
from uuid import uuid4
import json

region_name = getenv('APP_REGION')
blog_blog_table = boto3.resource('dynamodb', region_name=region_name).Table('BlogBlog2024')

def lambda_handler(event, context):
    http_method = event["httpMethod"]

    if "body" in event and event["body"] is not None:
        event = json.loads(event["body"])

    if http_method == "POST":
        return create_blog(event, context)
    elif http_method == "GET":
        return get_blog(event, context)
    elif http_method == "PUT":
        return update_blog(event, context)
    elif http_method == "DELETE":
        return delete_blog(event, context)
    pass

def create_blog(event, context):
    pass

def get_blog(event, context):
    pass

def update_blog(event, context):
    pass

def delete_blog(event, context):
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