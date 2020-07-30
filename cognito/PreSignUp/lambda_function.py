import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_REGION = "ca-central-1"
client = boto3.client('ses',region_name=AWS_REGION)
CHARSET = "UTF-8"

# this email needs to be verified with SES Service
SENDER = ""


def lambda_handler(event, context):
    logger.info(event)
    
    if event['request']['userAttributes'].get('user_type', '') == 'ADMIN':
        event['response']['autoConfirmUser'] = True
    elif event['request']['userAttributes'].get('user_type', '') == 'MENTEE':
        event['response']['autoConfirmUser'] = True
    else:
        event['response']['autoConfirmUser'] = False
        RECIPIENT = event['request']['userAttributes']['email']
        
        SUBJECT = "Welcome to MAX Aspire"
        BODY_TEXT = ("Welcome to MAX Aspire\r\n"
                     "Thanks for joining our mentor family "
                     "Please allow a few days before we verify your account."
                    )
        BODY_HTML = """<html>
        <head></head>
        <body>
          <h1>Amazon SES Test (SDK for Python)</h1>
          <p>Thanks for joining our mentor family
            Please allow a few days before we verify your account.</p>
        </body>
        </html>
                    """
        
        try:
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,
            )
        except ClientError as e:
            logger.info(e.response['Error']['Message'])
        else:
            logger.info("Email sent! Message ID:"),
            logger.info(response['MessageId'])
    
    return event
