import boto3
from boto3.dynamodb.conditions import Key
from os import getenv
from uuid import uuid4
import json

region_name = getenv('APP_REGION')
blog_post_table = boto3.resource('dynamodb', region_name=region_name).Table('BlogPost')


def lambda_handler(event, context):
    http_method = event["requestContext"]["http"]["method"]

    if http_method == "POST":
        return create_post(event, context)
    elif http_method == "GET":
        return get_post(event, context)
    elif http_method == "PUT":
        return update_post(event, context)
    elif http_method == "DELETE":
        return delete_post(event, context)
    else:
        return response(400, "invalid http method")


def create_post(event, context):
    if "body" in event and event["body"] is not None:
        body = json.loads(event["body"])

    blog_id = event["pathParameters"]["blog_id"]

    post_id = str(uuid4())
    # user_id = body["user_id"]
    title = body["title"]
    content = body["content"]

    blog_post_table.put_item(Item={
        "Id": post_id,
        "blog_id": blog_id,
        # "user_id": user_id,
        "title": title,
        "content": content
    })

    return response(200, {"post_id": post_id, "message": "Post successfully created!"})


def get_post(event, context):
    if "pathParameters" not in event:
        return response(400, {"error": "no path params"})

    path = event["pathParameters"]

    if path is None or "id" not in path:
        return response(400, "no id found")

    post_id = path["id"]

    post = blog_post_table.get_item(Key={"Id": post_id})["Item"]

    return response(200, post)


def update_post(event, context):
    if "body" in event and event["body"] is not None:
        body = json.loads(event["body"])

    post_id = event["pathParameters"]["post_id"]
    title = body["title"]
    content = body["content"]

    post = blog_post_table.get_item(Key={"Id": post_id})["Item"]

    if post_id is None:
        return response(404, "Post not found")
    if title is not None:
        post['title'] = title
    if content is not None:
        post['content'] = content

    blog_post_table.put_item(Item=post)

    return response(200, post)


def delete_post(event, context):
    if "pathParameters" not in event:
        return response(400, {"error": "no path params"})

    path = event["pathParameters"]

    if path is None or "post_id" not in path:
        return response(400, "no post_id found")

    post_id = path["post_id"]

    output = blog_post_table.delete_item(Key={"Id": post_id})

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
