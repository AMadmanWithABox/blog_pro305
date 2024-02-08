import boto3
from boto3.dynamodb.conditions import Key
from os import getenv
from uuid import uuid4
import json

region_name = getenv('APP_REGION')
blog_user_table = boto3.resource('dynamodb', region_name=region_name).Table('BlogUser2024')


def lambda_handler(event, context):
    http_method = event["httpMethod"]

    if "body" in event and event["body"] is not None:
        event = json.loads(event["body"])

    if http_method == "POST":
        return create_user(event, context)
    elif http_method == "GET":
        return get_user(event, context)
    elif http_method == "PUT":
        return update_user(event, context)
    elif http_method == "DELETE":
        return delete_user(event, context)
    else:
        return response(400, "invalid http method")


def create_user(event, context):
    user_id = str(uuid4())
    username = event["username"]
    password = event["password"]

    blog_user_table.put_item(Item={
        "Id": user_id,
        "username": username,
        "password": password
    })


def get_user(event, context):
    if "pathParameters" not in event:
        return response(400, {"error": "no path params"})

    path = event["pathParameters"]

    if path is None or "id" not in path:
        return response(400, "no id found")

    id = path["id"]

    user = blog_user_table.get_item(Key={"Id": id})["Item"]

    return response(200, user)


def update_user(event, context):
    id = event["id"]
    username = event["username"]
    password = event["password"]

    user = blog_user_table.get_item(Key={"Id": id})["Item"]

    if id is None:
        return response(404, "User not found")
    if username is not None:
        user['username'] = username
    if password is not None:
        user['password'] = password

    blog_user_table.put_item(Item=user)

    return response(200, user)


def delete_user(event, context):
    if "pathParameters" not in event:
        return response(400, {"error": "no path params"})

    path = event["pathParameters"]

    if path is None or "id" not in path:
        return response(400, "no id found")

    id = path["id"]

    output = blog_user_table.delete_item(Key={"Id": id})

    return response(200, output)


def response(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body),
        "isBase64Encoded": False
    }