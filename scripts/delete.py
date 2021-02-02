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
    - city
    - user_type
    - declared_chats_freq
    - remaining_chats_freq
    - phone_number
    - start_date
    - end_date

missing fields:
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
from botocore.config import Config

# TODO: create tool that will take a format of a command line input (below) and create the arg parsers for it
parser = argparse.ArgumentParser(description='add/remove SEs and populate Chat table from CSV')
parser.add_argument('-file', type=lambda x: is_valid_file(parser, x), required=True, help='Relative Path to CSV file')
parser.add_argument('-images_folder', type=str, required=True, help='Relative Path to images folder.')
parser.add_argument('-rows', type=int, required=True, help='Number of SEs in CSV file')
parser.add_argument('-pool_id', type=str, required=True, help='Cognito User Pool Id')
parser.add_argument('-id_token', type=str, required=False, help='Cognito Id Token (Admin Required)')
parser.add_argument('-users_list', type=str, nargs='+', help='only process listed users\' emails')

commands_group = parser.add_mutually_exclusive_group(required=True)
commands_group.add_argument('-create', action='store_true', help='Create SEs and/or Chats')
commands_group.add_argument('-delete', action='store_true', help='Delete SEs and/or Chats')
commands_group.add_argument('-create_clean', action='store_true', help='Delete and Create SEs and/or Chats')
commands_group.add_argument('-upload_images', action='store_true', help='Upload SEs images in S3')

options_group = parser.add_mutually_exclusive_group(required=True)
options_group.add_argument('-a', '--all', action='store_const', dest='type', const='all', help='Process Users and Chats')
options_group.add_argument('-u', '--users', action='store_const', dest='type', const='users', help='Process Users Only')
options_group.add_argument('-c', '--chats', action='store_const', dest='type', const='chats', help='Process Chats Only')

my_config = Config(
        region_name = 'us-east-1'
    )
aws_client = boto3.client('cognito-idp', config=my_config)
s3 = boto3.resource('s3')

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

# docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html#CognitoIdentityProvider.Client.admin_delete_user
def admin_delete_user(user, poolId):
    print("delete user: " + user)
    try:
        response = aws_client.admin_delete_user(
            UserPoolId=poolId,
            Username=user
        )
        # print("response= {}".format(response))
        return response
    except:
        #traceback.print_exc()
        return None
    return None
# --- COGNITO APIs END ---


def delete_user(user, poolId):
    #if len(user['email'].split(';')) > 1:
    #    user['email'] = user['email'].split(';')[0]
    admin_delete_user(user, poolId)

def delete_user_chats(user_chats, poolId):
    if len(user_chats['email'].split(';')) > 1:
        user_chats['email'] = user_chats['email'].split(';')[0]
    print("delete user chats: {}".format(user_chats['email']))

    response = requests.delete(
        # url='https://nv4pftutrf.execute-api.us-east-1.amazonaws.com/Prod/chats/create-multiple',
        url='http://127.0.0.1:3000/chats',
        params={'senior_executive': user_chats['email']},
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % (args.id_token)
        }
    )
    if response.status_code != 200:
        print("chats deletion for user {} failed. {}".format(user_chats['email'], response))

def delete_all(users, poolId):
    if users:
        for u in users:
            delete_user(u, poolId)
            time.sleep(1)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("file %s does not exist!" % arg)
    else:
        return os.path.abspath(arg)

 
# --- HELPERS END---

if __name__ == "__main__":
    users = ["3a096672-f40c-4519-abdf-a68aa34c5aed",
"0dd145fb-b02d-4a47-82ef-b6e4755c04ea",
"e5bff37a-9c33-4dab-b80b-723fce0694e6",
"9bccf5a4-7f8c-44ba-9dc2-fcabcaead381",
"abcccb09-aa1c-495f-aa15-cc47db257a37",
"8387d3e5-2a49-4d52-972d-1923428bb576",
"696a2df6-9255-4f43-8460-34b2525d5a7a",
"c79f75db-bfd2-40ec-ac35-6844ca33091c",
"78e99d68-01c9-471c-809e-46b02e7f2df9",
"ee63f579-e1d5-4c93-95a4-6d7ad41c3cfd",
"18351052-90eb-4250-844f-4c0ae97e0aab",
"6c5877ef-3075-4ff8-9a97-d5793d6c4420",
"7b04362c-da05-4182-b15b-e77cef56a27d",
"fc7beec1-5151-41e2-876f-ea3493c9c92d",
"0dc3a645-5406-4b31-bd84-3f3de50fffed",
"1f7e3df6-7340-4e04-9027-12ca5314891b",
"a915a501-5dfd-49ae-b9ae-f1dc701e9b18",
"5d200212-24a2-45cd-8475-3d1b4cf8bc0f",
"daba3af5-0170-4ebf-a505-8ba90e964ef8",
"4aef4644-a5bb-4d27-8ddb-eba3db9abc4f",
"c125ea82-8713-4b41-b221-9de074b66d46",
"e38a4e61-6a0f-40cb-be94-56a530bab6ea",
"d07585b8-5e60-483b-985e-ec061e3175de",
"2dac59d2-5031-48ad-add4-4b7407a0109c",
"420e8260-c732-4fce-a889-0c721db6b2c8",
"5c1504e3-94a1-4a6a-b895-f0ff728846bf",
"1e240b3d-7133-4635-a99c-976fdfbde813",
"da824201-1d10-46bd-bc6d-0344288112f8",
"925ce92c-3711-41a8-a028-bb8269b8629a",
"25ad0bfd-5191-4315-b1f0-3fbc28de55e7",
"6be7f03a-579b-4fe5-a98b-e916b55caf98",
"933ffc0e-b7ab-480e-9808-b226f98e83f4",
"29b387ae-1f79-463c-88b1-bfd51c59bc02",
"cdcbd0d4-7322-4f57-aadc-72fafd0cbe6a",
"9fbfeb5d-3597-4479-a93f-7d3ca0df6314",
"fa28c089-f51a-4caf-bb6e-dbc658b65626",
"76cfda1e-c3d7-43ca-abb6-100db4febf7e",
"4249d0bc-fd95-4afc-9d4c-45efab1a2ff3",
"203898d9-68be-480a-b557-406b6b15f9cc",
"7ffa5e74-d0e7-46e6-ab2c-bfd215b29a7e",
"de677f43-64d1-40af-933b-473b91b463aa",
"6cc123c1-86db-4da6-bc00-959f0c0ba8f1",
"1f5f7121-ddd7-48c1-ad0f-5b58d568e0c6",
"fe11fe7e-80e0-4715-8d6e-3a7ce65500c4",
"320de183-b4fc-40b0-b999-af2420e3f437",
"ec2f80d4-ffe6-4144-a677-75611d0b373c",
"32dab6e7-9bfc-49a6-aefd-b8235577c8c4",
"c475c5f3-629f-49f4-8f2e-ba30dd1fcf6d",
"a3b93a73-6496-4621-96d7-58aa73b46043",
"29b3526d-99b8-4812-ac10-1a239cb3a5c6",
"9067ed96-c377-4dc8-8305-a34ddf2a6de4",
"860eaf1f-86fe-4ac1-80a7-f1b4fdc3519b",
"4c9ddf2f-b13c-4fdf-96aa-8a077e8fb566",
"c2496f1a-b967-4d1a-b644-088cbc6c7795",
"fa0091b4-6ce2-4b7f-8748-acfd4c41a2b5",
"88de248a-16ad-4e5f-9222-377f6ec96a75",
"c30c83f3-2e9e-46d2-afd9-330e4b2642e8",
"15a1f849-0381-4cce-a8b1-70329f5fd9c6",
"62127f1e-6877-4790-8f64-dc5890650129",
"1d2550d3-e65f-487e-94e0-de8659b82cbb",
"6dc62158-838c-4a40-82d5-3c29e4f2bb99",
"79086eaf-1f7a-4d19-aecb-2f6d6753dffb",
"7b4e08a3-3d72-4f0d-b854-47418f83cbfa",
"07774429-4a5c-4b0d-a25d-eb3faf8b431a",
"4d357df7-eda1-43f2-a653-f392da5cb49b",
"a6899572-d3ba-424c-b366-8c2ca0f78692",
"52e7a22a-2b49-46ff-a7ed-13beb31a481c",
"9ed432ba-f2bc-4cda-9061-e9ab7e1fed6b",
"755b3362-f573-4b60-bf4c-6317cb3b90c3",
"f3d72047-89b1-4aaa-9ec2-6d33eee10c00",
"3aa58cf6-4aac-454f-9f29-a908db35dd1f",
"9cdb1d88-3521-42ad-804f-c1ba43cb5932",
"c6c319f8-0a06-4eb0-9b53-e11fc8d24aa6",
"48cf44fa-8553-4dcf-87b9-ee8922307cb3",
"df5e4914-fdc7-4279-80ad-e7d9157547eb",
"b280e3c6-08cf-4e3b-a636-7975ee8a5ead",
"96db2a14-8eca-45a6-87db-d44a60608a2e",
"910577b0-1110-41cc-85df-87a9c90ea7f0",
"59705c81-71fb-410d-9ded-228cc0ee3c6c",
"d5392932-e77f-47df-8e2d-38f2cb18b3fe",
"f5622256-9aad-46ae-8ecc-a167e49e0b8d",
"75e26e87-52ad-4d26-8251-ef3a64a83c6c",
"a06c848d-1186-44ab-9a30-f05987ae5e44",
"79e7b1e6-9148-4f36-8d7a-15efa41fc84e",
"4b43482e-7101-4ec0-85c5-075797a16103",
"b8ec2c0a-10d5-442e-9968-3b720b8ede4b",
"e90a1ea4-ba8d-44b8-9e49-867abd94be88",
"f9033939-a032-4f1c-a035-e79dff1a3ce9",
"e79ac3e8-c740-41e2-adb1-ed7fd4b3e3cc",
"91597da8-8497-47eb-882f-6bbfde5263ba",
"ce29a49f-eca9-44a6-9479-76886c36cffa",
"a23ba077-660a-4a5c-8bb5-fbbf9284b419",
"199c4786-1ffa-4ec3-a877-96f4fb4e96e7",
"a5799ca2-7707-47be-947e-4f05744bb512",
"83eded01-b715-4d66-a8a7-e5aa0d5e716d",
"86a3f112-6394-4f60-88e1-a4a12f45f3ad",
"d1e8db42-893e-49d6-ad46-a9f6c59edeac",
"a3e0aadb-c1ed-4d66-939c-72f5cbcb1bc2",
"0c57be1b-a97e-4bb7-8534-adda7d65ebd5",
"5a37c784-4b26-43dd-a04c-06e9379aae88",
"7b6f1c40-4a07-410a-836e-f1ce443ab8fa",
"86024ee1-1032-4a02-9da2-dc4c0b27dc48",
"d956e03b-04b0-4e37-b38d-70ac94fc8785",
"6a15fa70-3983-4fe2-9b0d-6c0fb6036498",
"ac94ac22-74db-4ecc-8a2a-8aab7d9e6101",
"60d51c0e-0e4d-4ab5-a520-50774bae270b",
"12bfc5fc-edbb-4ca6-a46f-1ec4dbc1dc72",
"53fcca05-829c-4383-9a00-16b03a110f84",
"51c6ebee-086e-42bb-bc22-c289db384115",
"a8bed8f1-0d2d-4b71-8441-c86a583821a3",
"e173e36c-03e3-4a6f-85ab-a220ed0ce1b2",
"e3fc9d42-7fcf-4ba2-88e8-705f0287a443",
"cea2281c-8db3-4a23-8e14-c27a19c3f093",
"b953f808-5f8d-4347-85b9-90bba00be003",
"b119c754-ea1a-4923-ac33-87b2c94f27a6",
"3d02cca9-88f0-42c4-92e9-6160f36061cc",
"393b22ad-2a25-473b-92b4-5184f39b0e05",
"74144907-8c0e-4e53-add2-a43a73364255",
"7c9767b1-4e05-44c1-bd84-6cbef06c12b3",
"ec351f15-1eaf-4a8b-b832-55cabbe84095",
"4d443132-71e5-4930-96bd-da4096b2eafb",
"3f4b3d74-8b11-4722-8d71-9528ebebb396",
"3225989d-be22-400d-b7c0-7de993eabbe6",
"cd04dc00-cdb8-4dc3-b644-c2c763e04a5a",
"43e1e61e-b33e-4eca-92b0-154f93ba3b33",
"be3e1772-17f5-4fa0-a243-a0498fb64fb3",
"7184c7e0-b42c-448d-b199-fb7d913dc126",
"4f33c989-f00a-4e73-9257-69bb7065a996",
"28fc92ad-e91b-4631-8ce9-e65e43bdaf44",
"3aa2bda8-3dcd-42e4-8e48-5db5de6f30f5",
"1facafda-eba5-49ec-a75c-29e0884a3453",
"f97f94f5-6f8c-4042-9a22-bba0d86c2abe",
"34e70b1b-32b3-40cd-9ebd-567fe0cb4cb4",
"a2f6c346-64f2-463a-8aa8-d2c1c6e14a3e",
"368676b3-8d7d-46c8-a357-d7b56af39bf7",
"36c6feda-d8c6-496c-866f-ac7c7a308ad6",
"f2c5263d-d0e6-43b4-931e-2e9c0171ec48",
"8721913d-ee78-4ecd-8cd3-b7da77989fef",
"5cc86c64-8c76-4cb7-9008-70392845da14",
"c6c032d3-c10d-4c60-b604-e90ae76f89cc",
"948d80cb-2974-4e0d-ba68-c7c1ffe6906c",
"81ec091f-6285-4992-86c4-006b797c9af0",
"22380706-b371-40c3-be4b-69606b07e4af",
"e2596ea6-b11f-4122-9dff-6bc7303832ee",
"1dcda25c-a0f6-4345-9070-492b7bcec536",
"b2f7b45b-a564-45ba-8d44-3c84ddb0c321",
"45b8da92-4c29-42eb-bc6f-f3d94725aad9",
"38efe4dc-7106-434a-bc62-23389c34c09c",
"e07a63bc-0dbb-494c-af4c-8a0a40594e9b",
"307937c6-f600-4371-b7f5-34116c691db6",
"82b5ed11-717b-410c-bc36-51dbd07a708b",
"114d06ef-35f9-4e1d-9be4-fa5eca41d849",
"ea5ace69-d1e5-47ef-86ac-84e2700e01dc",
"e2e7aaca-5b68-46c3-9ed5-4adde866a963",
"842b4626-71ad-4d95-92ed-880afb0918aa",
"b81e9452-4a2a-430f-a57f-3f2107624935",
"a1125bc5-8f15-41d0-8623-80173bbdfa90"]

    delete_all(users,"us-east-1_dq5r8O2SO")
    #for user in users:
    #    print(user)
    
    exit(1)
    """args = parser.parse_args()

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
    
    if args.upload_images:
        upload_images(users_records,args.images_folder, args.pool_id)
    elif args.create:
        create_all(users_records, users_chats_records, args.pool_id)
    elif args.delete:
        delete_all(users_records, users_chats_records, args.pool_id)
    else:
        delete_all(users_records, users_chats_records, args.pool_id)
        create_all(users_records, users_chats_records, args.pool_id)"""
