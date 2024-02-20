import boto3
from boto3.dynamodb.conditions import Key
from os import getenv
from uuid import uuid4
import json

region_name = getenv('APP_REGION')
blog_blog_table = boto3.resource('dynamodb', region_name=region_name).Table('BlogBlog')


#   This lambda will be locked down to only authenticated users, so we don't need to check for that here,
#   but we still need to check the http method
def lambda_handler(event, context):
    http_method = event["httpMethod"]

    if http_method == "POST":
        return create_blog(event, context)
    elif http_method == "GET":
        return get_blog(event, context)
    elif http_method == "PUT":
        return update_blog(event, context)
    elif http_method == "DELETE":
        return delete_blog(event, context)
    else:
        return response(400, "invalid http method")


def create_blog(event, context):
    if "body" in event and event["body"] is not None:
        body = json.loads(event["body"])

    user_guid = event['requestContext']['authorizer']['user_guid']

    blog_id = str(uuid4())
    title = body["title"]
    category = body["category"]
    description = body["description"]

    blog_blog_table.put_item(Item={
        "Id": blog_id,
        "user_guid": user_guid,
        "title": title,
        "category": category,
        "description": description,
        "subscribers": []
    })

    return response(200, {"blog_id": blog_id, "message": "Blog successfully created!"})


def get_blog(event, context):
    if "pathParameters" not in event:
        return response(400, {"error": "no path params"})

    path = event["pathParameters"]

    if path is None or "id" not in path:
        return response(400, "no id found")

    blog_id = path["id"]

    blog = blog_blog_table.get_item(Key={"Id": blog_id})["Item"]

    return response(200, blog)


def update_blog(event, context):
    if "body" in event and event["body"] is not None:
        event = json.loads(event["body"])

    blog_id = event["id"]
    if blog_id is None:
        return response(400, "Blog id not found")

    blog = blog_blog_table.get_item(Key={"Id": blog_id})["Item"]
    if blog is None:
        return response(400, "Blog not found")

    user_guid = event['requestContext']['authorizer']['user_guid']
    if blog['user_guid'] != user_guid:
        return response(401, "Unauthorized")

    title = event["title"]
    category = event["category"]
    description = event["description"]

    if title is not None:
        blog['title'] = title
    if category is not None:
        blog['category'] = category
    if description is not None:
        blog['description'] = description

    blog_blog_table.put_item(Item=blog)

    return response(200, blog)


def delete_blog(event, context):
    if "pathParameters" not in event:
        return response(400, {"error": "no path params"})

    path = event["pathParameters"]

    if path is None or "blog_id" not in path:
        return response(400, "no blog_id found")

    blog_id = event["id"]

    blog = blog_blog_table.get_item(Key={"Id": blog_id})["Item"]
    if blog is None:
        return response(400, "Blog not found")

    user_guid = event['requestContext']['authorizer']['user_guid']
    if blog['user_guid'] != user_guid:
        return response(401, "Unauthorized")

    output = blog_blog_table.delete_item(Key={"Id": blog_id})

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
