'''
This script reads a csv file of MAX Aspire senior professionals and manually adds then to the user pool
run with help command to get help running this script

see: https://github.com/maxgala/aspire-infra/blob/master/cfn_cognito.yaml
AND  docs/senior_professionals
fields:
    - email
    - family_name
    - given_name
    - gender
    - industry_tags
    - position
    - company
    - country
    - region

missing fields:
    - phone_number
    - birthdate
    - education_level
    - resume
    - picture
    - linkedin_link
    - credits
'''

import traceback
import boto3
import json

aws_client = boto3.client('cognito-idp')

# AWS Cognito standard attributes. Every user will have them by default (even if not used)
# docs: https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-attributes.html
standard_attributes = [
    'address', 'birthdate', 'email', 'family_name', 'gender', 'given_name', 'locale', 
    'middle_name', 'name', 'nickname', 'phone_number', 'picture', 'preferred_username', 
    'profile', 'updated_at', 'website', 'zoneinfo'
]

# --- COGNITO APIs BEGIN ---

# docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html#CognitoIdentityProvider.Client.admin_create_user
def admin_create_user(user: dict, poolId: str):
    print("sign up user: {}".format(user['email']))
    try:
        response = aws_client.admin_create_user(
            UserPoolId=poolId, 
            Username=user['email'], 
            UserAttributes=[
                {'Name': key, 'Value': val} if key in standard_attributes \
                    else {'Name': 'custom:{}'.format(key), 'Value': val} for key, val in user.items() if val
            ], 
            DesiredDeliveryMediums=['EMAIL'], 
            MessageAction='SUPPRESS'
        )
        print("response= {}".format(response))
        return response
    except:
        traceback.print_exc()
    return None

def admin_get_user(user: dict, poolId: str):
    print("get user: {}".format(user['email']))
    try:
        response = aws_client.admin_get_user(
            UserPoolId=poolId, 
            Username=user['email']
        )
        print("response= {}".format(response))
        return response
    except:
        traceback.print_exc()
    return None

def admin_delete_user(user: dict, poolId: str):
    print("delete user: {}".format(user['email']))
    try:
        response = aws_client.admin_delete_user(
            UserPoolId=poolId, 
            Username=user['email']
        )
        print("response= {}".format(response))
        return response
    except:
        traceback.print_exc()
    return None
    
# --- COGNITO APIs END ---

# --- HELPERS BEGIN---
def create_one(user: dict, poolId: str):
    if not user['email']:
        return

    user['address'] = json.dumps({'country': user.pop('country'), 'region': user.pop('region')})
    admin_create_user(user, poolId)

def create_all(users: list, poolId: str, delall=False):
    if(delall):
        delete_all(users, poolId)

    for user in users:
        create_one(user, poolId)

def delete_one(user: dict, poolId: str):
    admin_delete_user(user, poolId)

def delete_all(users: list, poolId: str):
    for user in users:
        delete_one(user, poolId)

# --- HELPERS END---

if __name__ == "__main__":
    import sys
    import os
    import pandas as pd
    
    def help():
        return '''  Usage: python add_mentors.py <command> {csv_file_relative_path} {number_of_mentors} {AWS_Cognito_UserPoolId} [options]
          Commands can be one of the following:
            * create_all
            * delete_all
            * help
          Options:
            * -d: delete all users before creation flag. Only usable with create_all command
          Notes:
            * supports python 3
            * aws profile with admin permissions
            * keep col_list updated
        '''
    def error_exit():
        print(help())
        exit(1)
    
    command = sys.argv[1] if len(sys.argv) > 1 else error_exit()
    if command == 'help':
        print(help())
        exit(0)
    
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print(help())
        exit(1)
    
    file_path = sys.argv[2]
    num_mentors = int(sys.argv[3])
    poolId = sys.argv[4]

    col_list = ['email', 'family_name', 'given_name', 'prefix', 'gender', \
        'age_range', 'industry_tags', 'position', 'company', 'country', 'region']
    mentors_df = pd.read_csv(os.path.abspath(file_path), header=1, usecols=col_list, nrows=num_mentors, engine='python', keep_default_na=False)
    mentors_list = mentors_df.to_dict('records')

    if (command == 'create_all'):
        if len(sys.argv) > 5:
            if sys.argv[5] == '-d':
                delall = True
            else:
                print(help())
                exit(1)
        else:
            delall = False
        create_all(mentors_list, poolId, delall=delall)
    elif (command == 'delete_all'):
        delete_all(mentors_list, poolId)
    else:
        print(help())
        exit(1)
    
    exit(0)
