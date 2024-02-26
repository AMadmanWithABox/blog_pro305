import json

import boto3
from base64 import b64decode
import re
import os

# Initialize DynamoDB resource
region_name = os.getenv('APP_REGION')
blog_user_table = boto3.resource('dynamodb', region_name=region_name).Table('BlogUser')


def lambda_handler(event, context):

    try:
        auth_header = event['headers'].get("Authorization")
        if not auth_header:
            raise ValueError("Authorization header is missing")

        matcher1 = re.match("^Basic (.+)$", auth_header)
        if not matcher1:
            raise ValueError("Invalid Authorization header format")

        credentials = b64decode(matcher1.group(1)).decode('utf-8')
        username, password = credentials.split(':')

        user_id, effect = found_in_db(username, password)
        if effect == "Allow":
            return generate_policy(effect, user_id)
        else:
            raise Exception('Unauthorized')

    except Exception as e:
        print(f"Error: {str(e.with_traceback(None))}")
        return generate_policy('Deny', None)


def found_in_db(username, password):
    response = blog_user_table.scan(
        FilterExpression="username = :username AND password = :password",
        ExpressionAttributeValues={
            ':username': username,
            ':password': password
        }
    )

    if len(response["Items"]) == 1:
        user_id = response["Items"][0].get("Id")  # Assuming 'user_guid' is the attribute name in your DynamoDB table
        return user_id, "Allow"
    else:
        return None, "Deny"


def generate_policy(effect, user_id):
    isAuthorized = effect == "Allow"
    auth_response = {
        # "principalId": principal_id,
        # "policyDocument": {
        #     "Version": "2012-10-17",
        #     "Statement": [{
        #         "Action": "execute-api:Invoke",
        #         "Effect": effect,
        #         "Resource": resource
        #     }]
        # },
        "isAuthorized": isAuthorized,
        "context": {
            "user_id": user_id
        } if isAuthorized else {}
    }

    print(f"Auth Response: {json.dumps(auth_response, indent=2)}")
    return auth_response
