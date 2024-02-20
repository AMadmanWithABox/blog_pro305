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

        if found_in_db(username, password):
            effect = "Allow"
        else:
            effect = "Deny"

        return generate_policy('user', effect, event['methodArn'])

    except Exception as e:
        print(f"Error: {str(e)}")
        raise Exception('Unauthorized')


def found_in_db(username, password):
    # Ideally, use a more efficient query here if your table design allows
    response = blog_user_table.scan(
        FilterExpression="username = :username AND password = :password",
        ExpressionAttributeValues={
            ':username': username,
            ':password': password
        }
    )
    return len(response["Items"]) == 1


def generate_policy(principal_id, effect, resource):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": resource
            }]
        }
    }
