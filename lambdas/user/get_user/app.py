import boto3
from boto3.dynamodb.conditions import Key
from os import getenv
from uuid import uuid4
import json

region_name = getenv('APP_REGION')
blog_user_table = boto3.resource('dynamodb', region_name=region_name).Table('BlogUser2024')


def lambda_handler(event, context):

    if ( ("pathParameters" in event) ):

        path = event["pathParameters"]

        if path is None or "id" not in path:
            return response(200, blog_user_table.scan()["Items"])

        if path is not None and "id" in path:
            id = path["id"]
            output = blog_user_table.get_item(Key={"Id":id})["Item"]
            return response(200, output)

    return response(200, blog_user_table.scan()["Items"])



def response(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json"
            },
        "body": json.dumps(body),
        "isBase64Encoded": False
    }