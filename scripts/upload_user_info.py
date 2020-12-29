###  Takes in a json file and creates a json file containing info in s3


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

parser = argparse.ArgumentParser(description='add user info to s3 bucket')
parser.add_argument('-file', type=lambda x: is_valid_file(parser, x), required=True, help='Relative Path to json file')

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("file %s does not exist!" % arg)
    else:
        return os.path.abspath(arg)

if __name__ == "__main__":
    s3 = boto3.resource('s3')
    bucket_name = "aspire-user-profile"
    args = parser.parse_args()
    with open(args.file) as f:
        data = json.load(f)
    for user in data:
        user['email'] = user['email'].split(';')[0]
        print("uploading user info for: " + user["email"])
        
        folder_path = user["email"] + "/info.json"
        
        try:
            s3object = s3.Object(bucket_name, folder_path)
            s3object.put(
                Body=json.dumps(user),
                ACL = 'public-read',
                ContentType='json'
            )
        except:
            print("error while uploading info")
        
