import boto3
from os import getenv
import os
import json

region_name = getenv('APP_REGION')
cognito_client = boto3.client('cognito-idp', region_name=region_name)

# Access the User Pool ID from environment variables
USER_POOL_ID = os.getenv('USER_POOL_ID')


def lambda_handler(event, context):
    http_method = event["requestContext"]["http"]["method"].upper()
    print(http_method)

    if http_method == "POST":
        return create_user(event, context)
    elif http_method == "GET":
        return get_user(event, context)
    elif http_method == "PUT":
        return update_user(event, context)
    elif http_method == "DELETE":
        return delete_user(event)
    else:
        return response(400, "Invalid HTTP method")


def create_user(event, context):
    try:
        # Parse the JSON body to get the username and password
        body = json.loads(event["body"])
        username = body["username"]
        password = body["password"]

        # Call Cognito to create the user with just the username and temporary password
        user = cognito_client.admin_create_user(
            UserPoolId=USER_POOL_ID,
            Username=username,
            TemporaryPassword=password,  # Consider using secure methods for setting initial passwords
            MessageAction='SUPPRESS'  # Optionally suppress the welcome email
        )
        # Extract the user's ID (sub) from the response
        user_id = next(attr['Value'] for attr in user['User']['Attributes'] if attr['Name'] == 'sub')

        return response(200, {"message": "User successfully created", "Username": username, "UserId": user_id})
    except Exception as e:
        return response(400, {"error": str(e)})


def get_user(event):
    path_parameters = event.get('pathParameters', {})

    if 'username' in path_parameters:
        # Fetch user by username
        return get_user_by_username(path_parameters['username'])
    else:
        # Fetch all users
        return get_all_users()


def get_user_by_username(username):
    try:
        user = cognito_client.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=username
        )
        # Extract required details
        user_details = {
            'Username': user['Username'],
            'Attributes': user['UserAttributes']
        }
        return response(200, user_details)
    except Exception as e:
        return response(400, {"error": str(e)})


def get_all_users():
    # Use list_users to fetch all users. Note: this might need pagination handling for a large number of users.
    try:
        users = cognito_client.list_users(UserPoolId=USER_POOL_ID)
        # Simplify the response to include only necessary details like Username and possibly UserAttributes
        simplified_users = [{'Username': user['Username']} for user in users['Users']]
        return response(200, simplified_users)
    except Exception as e:
        return response(400, {"error": str(e)})


#   Only the user can update their own account, we grab their guid by get_user_by_username_password(username, password):
def update_user(event, context, user_id):
    # Parse the incoming event
    if "body" in event and event["body"] is not None:
        body = json.loads(event["body"])
        username = body.get("username")
        new_password = body.get("password")

    # Check if username is provided and non-empty
    if not username or not username.strip():
        return response(400, "Username is required and cannot be empty")

    user_attributes_update_list = []

    # Update user attributes if any are provided
    if user_attributes_update_list:
        try:
            cognito_client.admin_update_user_attributes(
                UserPoolId=USER_POOL_ID,
                Username=username,
                UserAttributes=user_attributes_update_list
            )
        except Exception as e:
            return response(400, {"error": str(e)})

    # Check if password is provided and non-empty, then update it
    if new_password and new_password.strip():
        try:
            cognito_client.admin_set_user_password(
                UserPoolId=USER_POOL_ID,
                Username=username,
                Password=new_password,
                Permanent=True  # Set to False if you want the user to change the password at next sign-in
            )
        except Exception as e:
            return response(400, {"error": str(e)})

    return response(200, {"message": "User updated successfully"})


# Only the user can delete their own account, we grab their guid by get_user_by_username_password(username, password):
def delete_user(event):
    username = event.get("pathParameters", {}).get("username")
    if not username:
        return response(400, "Username is required")

    try:
        cognito_client.admin_delete_user(
            UserPoolId=USER_POOL_ID,
            Username=username
        )
        return response(200, {"message": "User successfully deleted"})
    except cognito_client.exceptions.UserNotFoundException:
        return response(404, {"error": "User not found"})
    except Exception as e:
        return response(400, {"error": str(e)})


def response(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body),
        "isBase64Encoded": False
    }
