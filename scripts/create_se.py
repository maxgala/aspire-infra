'''
This script reads a csv file of MAX Aspire senior professionals and manually adds then to the user pool
run with -h for more information on running the script

see: https://github.com/maxgala/aspire-infra/blob/master/cfn_cognito.yaml
AND  docs/senior_professionals
fields:
    - email
    - family_name
    - given_name
    - prefix
    - gender
    - birthdate
    - industry
    - industry_tags
    - position
    - company
    - country
    - region
    - user_type
    - declared_chats_freq
    - remaining_chats_freq
    - phone_number

missing fields:
    - city
    - start_date
    - end_date
    - education_level
    - resume
    - picture
    - linkedin
    - credits
'''
import os
import re
import json
import time
import enum
import boto3
import requests
import argparse
import traceback
import pandas as pd
from datetime import datetime

# TODO: create tool that will take a format of a command line input (below) and create the arg parsers for it
parser = argparse.ArgumentParser(description='add/remove SEs and populate Chat table from CSV')
parser.add_argument('-file', type=lambda x: is_valid_file(parser, x), required=True, help='Relative Path to CSV file')
parser.add_argument('-rows', type=int, required=True, help='Number of SEs in CSV file')
parser.add_argument('-id', type=str, required=True, help='Cognito User Pool Id')
parser.add_argument('-users_list', type=str, nargs='+', help='only process listed users\' emails')

commands_group = parser.add_mutually_exclusive_group(required=True)
commands_group.add_argument('-create', action='store_true', help='Create SEs and/or Chats')
commands_group.add_argument('-delete', action='store_true', help='Delete SEs and/or Chats')
commands_group.add_argument('-create_clean', action='store_true', help='Delete and Create SEs and/or Chats')

options_group = parser.add_mutually_exclusive_group(required=True)
options_group.add_argument('-a', '--all', action='store_const', dest='type', const='all', help='Process Users and Chats')
options_group.add_argument('-u', '--users', action='store_const', dest='type', const='users', help='Process Users Only')
options_group.add_argument('-c', '--chats', action='store_const', dest='type', const='chats', help='Process Chats Only')

aws_client = boto3.client('cognito-idp')
id_token = 'eyJraWQiOiJYRGVtUzZpaUcrNjlRQ1ZzMlJIRXorZldRUVIxNHJRQXJPNHVlbEwwVXM0PSIsImFsZyI6IlJTMjU2In0.eyJhdF9oYXNoIjoiRUVPdy0xNXdhU2d1NW55bkpwdlNyUSIsInN1YiI6IjYxMzQwMTJiLWNmZjgtNGE5ZS1iOTU4LTg4OTIyODBkZjM5MyIsImNvZ25pdG86Z3JvdXBzIjpbIkFETUlOIl0sImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhZGRyZXNzIjp7ImZvcm1hdHRlZCI6IjEyMyBUZXN0IFJvYWQifSwiYmlydGhkYXRlIjoiMjItMTEtMTk5NSIsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX240N1FUN0NxTyIsImNvZ25pdG86dXNlcm5hbWUiOiI2MTM0MDEyYi1jZmY4LTRhOWUtYjk1OC04ODkyMjgwZGYzOTMiLCJnaXZlbl9uYW1lIjoiU2FsZWgiLCJhdWQiOiI0NmoybmNhM2h2MDdxMG8waWNqdmRuZzlxbiIsImV2ZW50X2lkIjoiZmQ4MGI2OWMtOTYzMy00ZGFiLTk2ZjMtNDQ4NDgxOGIyNjIyIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2MDU5MDU0NDAsImV4cCI6MTYwNTkwOTA0MCwiaWF0IjoxNjA1OTA1NDQwLCJmYW1pbHlfbmFtZSI6IkJha2hpdCIsImVtYWlsIjoic2FsZWguYmFraGl0QGhvdG1haWwuY29tIn0.Z4xQnEw8jAmEI-8-QKCZfJt_Fc1vfHfFQ_bkuh07nipRdBi43sYAj0ai9AKymlKSBzmGGwv1r3LOoyg0fQOYmQ2Gez-7lHTC_C7ciBEqJxyHiyzSKqIA0PQiboZ5GNeTdIEQgC76WcsbdTcq5LEC30ifTmSNOuw-s9qxu7mWlFmSOLfZDFP4-_4576JfLGo67WmTmexK4ymI0-YpratCeDX-fPpr0FZWSVe0IqZRVcpSZupE3WNwhCEEm4s2eWqgLcC2uSYV1pyI1lgpaoxhyOPmG1akr4XKuhmIER-q_b2j25y7EBcCKy_BXyj89-4NBotXn08BtdbfWomlRj1K7g'

users_col_list = [
    'email', 'family_name', 'given_name', 'prefix', 'gender', 'industry',
    'industry_tags', 'position', 'company', 'country', 'region',
    'declared_chats_freq', 'phone_number'
]
users_chats_col_list = [
    'email', 'ONE_ON_ONE', 'FOUR_ON_ONE', 'MOCK_INTERVIEW'
]
# AWS Cognito standard attributes. Every user will have them by default (even if not used)
# docs: https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-attributes.html
standard_attributes = [
    'address', 'birthdate', 'email', 'family_name', 'gender', 'given_name', 'locale',
    'middle_name', 'name', 'nickname', 'phone_number', 'picture', 'preferred_username',
    'profile', 'updated_at', 'website', 'zoneinfo'
]


class ChatType(enum.Enum):
    ONE_ON_ONE = 1
    FOUR_ON_ONE = 2
    MOCK_INTERVIEW = 3


# --- COGNITO APIs BEGIN ---
def admin_add_user_to_group(username: str, group_name: str, poolId: str):
    print("add user to group: {} {}".format(username, group_name))
    try:
        response = aws_client.admin_add_user_to_group(
            UserPoolId=poolId,
            Username=username,
            GroupName=group_name
        )
        # print("response= {}".format(response))
        return response
    except:
        traceback.print_exc()
    return None

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
        # print("response= {}".format(response))
        return response
    except Exception as e:
        if e.response['Error']['Code'] != 'UsernameExistsException':
            traceback.print_exc()
    return None

# docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html#CognitoIdentityProvider.Client.admin_get_user
def admin_get_user(user: dict, poolId: str):
    print("get user: {}".format(user['email']))
    try:
        response = aws_client.admin_get_user(
            UserPoolId=poolId,
            Username=user['email']
        )
        # print("response= {}".format(response))
        return response
    except:
        traceback.print_exc()
    return None

# docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html#CognitoIdentityProvider.Client.admin_delete_user
def admin_delete_user(user: dict, poolId: str):
    print("delete user: {}".format(user['email']))
    try:
        response = aws_client.admin_delete_user(
            UserPoolId=poolId,
            Username=user['email']
        )
        # print("response= {}".format(response))
        return response
    except:
        traceback.print_exc()
    return None
# --- COGNITO APIs END ---

# --- HELPERS BEGIN---
def create_user(user: dict, user_type: str, poolId: str):
    if len(user['email'].split(';')) > 1:
        user['email'] = user['email'].split(';')[0]

    if not user['phone_number']:
        del user['phone_number']
    else:
        if len(user['phone_number'].split(';')) > 1:
            user['phone_number'] = user['phone_number'].split(';')[0].strip()
        user['phone_number'] = re.sub(r'[\s-]', '', user['phone_number'].strip())
        if user['phone_number'][0] != '+':
            user['phone_number'] = '+1' + user['phone_number']

    user['address'] = json.dumps({'country': user.pop('country'), 'region': user.pop('region')})
    user['birthdate'] = '1970-01-01'
    user['user_type'] = user_type
    user['declared_chats_freq'] = '0'
    user['remaining_chats_freq'] = '0'
    user['credits'] = '0'
    admin_create_user(user, poolId)

def create_user_chats(user_chats: dict, delimiter=';'):
    if len(user_chats['email'].split(';')) > 1:
        user_chats['email'] = user_chats['email'].split(';')[0]
    print("create user chats: {}".format(user_chats['email']))

    user_chats['ONE_ON_ONE'] = user_chats['ONE_ON_ONE'].split(delimiter) if user_chats['ONE_ON_ONE'] != 'none' else []
    user_chats['FOUR_ON_ONE'] = user_chats['FOUR_ON_ONE'].split(delimiter) if user_chats['FOUR_ON_ONE'] != 'none' else []
    user_chats['MOCK_INTERVIEW'] = user_chats['MOCK_INTERVIEW'].split(delimiter) if user_chats['MOCK_INTERVIEW'] != 'none' else []

    chats = []
    for chat_type, chats_list in user_chats.items():
        if chat_type in ChatType.__members__ and chats_list:
            for fixed_date in chats_list:
                chats.append({
                    "chat_type": chat_type
                })
                if fixed_date != '':
                    # dated chat
                    chats[-1]['fixed_date'] = int(datetime.strptime(fixed_date, "%d/%m/%Y").timestamp())

    payload = json.dumps({
        "senior_executive": user_chats['email'],
        "chats": chats
    })
    response = requests.post(
        # url='https://nv4pftutrf.execute-api.us-east-1.amazonaws.com/Prod/chats/create-multiple',
        url='http://127.0.0.1:3000/chats/create-multiple',
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % (id_token)
        }
    )
    if response.status_code != 201:
        print("chats creation for user {} failed. {}".format(user_chats['email'], response))

def create_all(users: list, users_chats: list, poolId: str):
    if users:
        for u in users:
            if u['email']:
                create_user(u, 'MENTOR', poolId)
                admin_add_user_to_group(u['email'], 'MENTOR', poolId)
                time.sleep(1)
    if users_chats:
        for c in users_chats:
            if c['email']:
                create_user_chats(c)
                time.sleep(1)

def delete_user(user: dict, poolId: str):
    if len(user['email'].split(';')) > 1:
        user['email'] = user['email'].split(';')[0]
    admin_delete_user(user, poolId)

def delete_user_chats(user_chats: dict, poolId: str):
    if len(user_chats['email'].split(';')) > 1:
        user_chats['email'] = user_chats['email'].split(';')[0]
    print("delete user chats: {}".format(user_chats['email']))

    response = requests.delete(
        # url='https://nv4pftutrf.execute-api.us-east-1.amazonaws.com/Prod/chats/create-multiple',
        url='http://127.0.0.1:3000/chats',
        params={'senior_executive': user_chats['email']},
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % (id_token)
        }
    )
    if response.status_code != 200:
        print("chats deletion for user {} failed. {}".format(user_chats['email'], response))

def delete_all(users: list, users_chats: list, poolId: str):
    if users:
        for u in users:
            if u['email']:
                delete_user(u, poolId)
                time.sleep(1)
    if users_chats:
        for c in users_chats:
            if c['email']:
                delete_user_chats(c, poolId)
                time.sleep(1)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("file %s does not exist!" % arg)
    else:
        return os.path.abspath(arg)
# --- HELPERS END---

if __name__ == "__main__":
    args = parser.parse_args()

    users_records = None
    users_chats_records = None
    if args.type == 'users':
        users_df = pd.read_csv(os.path.abspath(args.file), header=1, usecols=users_col_list, nrows=args.rows, engine='python', keep_default_na=False)
        if args.users_list:
            users_df = users_df[users_df.email.str.contains('|'.join(args.users_list))]
        users_records = users_df.to_dict('records')
    elif args.type == 'chats':
        users_chats_df = pd.read_csv(os.path.abspath(args.file), header=1, usecols=users_chats_col_list, nrows=args.rows, engine='python', keep_default_na=False)
        if args.users_list:
            users_chats_df = users_chats_df[users_chats_df.email.str.contains('|'.join(args.users_list))]
        users_chats_records = users_chats_df.to_dict('records')
    else:
        users_df = pd.read_csv(os.path.abspath(args.file), header=1, usecols=users_col_list, nrows=args.rows, engine='python', keep_default_na=False)
        users_chats_df = pd.read_csv(os.path.abspath(args.file), header=1, usecols=users_chats_col_list, nrows=args.rows, engine='python', keep_default_na=False)
        if args.users_list:
            users_df = users_df[users_df.email.str.contains('|'.join(args.users_list))]
            users_chats_df = users_chats_df[users_chats_df.email.str.contains('|'.join(args.users_list))]
        users_records = users_df.to_dict('records')
        users_chats_records = users_chats_df.to_dict('records')

    if args.create:
        create_all(users_records, users_chats_records, args.id)
    elif args.delete:
        delete_all(users_records, users_chats_records, args.id)
    else:
        delete_all(users_records, users_chats_records, args.id)
        create_all(users_records, users_chats_records, args.id)
