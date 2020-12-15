import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cognito_client = boto3.client('cognito-idp')
ses_client = boto3.client('ses')

ADMIN_EMAIL = "aspire@maxgala.com"
SUPPORT_EMAIL = "aspire@maxgala.com"

CHARSET = "UTF-8"
SUBJECT = "Welcome to MAX Aspire!"

def send_email(source_email, to_addresses, subject, body_text, body_html, charset):
    try:
        response = ses_client.send_email(
            Destination={
                'ToAddresses': to_addresses,
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=source_email,
        )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
    else:
        logger.info("Email sent! Message ID:"),
        logger.info(response['MessageId'])

def handler(event, context):
    user_type =  event['request']['userAttributes'].get('custom:user_type', '')
    user_email = event['request']['userAttributes']['email']
    user_name = event['request']['userAttributes']['given_name']

    logger.info('confirming user {%s} with user_type {%s}' % (user_email, user_type))
    if user_type == 'ADMIN':
        # TODO: send email
        logger.info('disabling user of type {%s}' % (user_type))
        response = cognito_client.admin_disable_user(
            UserPoolId=event['userPoolId'],
            Username=event['userName']
        )
        logger.info(response)
    elif user_type == 'FREE':
        BODY_TEXT = (f"Salaam {user_name}!\r\n"
                     "\r\n\n"
                     "Welcome to MAX Aspire, our community of high achieving individuals aspiring for success. You have taken the first step to grow your career and develop a long lasting network and set of skills."
                     "On behalf of MAX Aspire, we welcome you and thank you for signing up.\r\n"
                     "\r\n\n"
                     "As an Aspiring Professional, here is how you can get started:\r\n"
                     "  - Book coffee chats with Senior Executives\r\n"
                     "  - Setup mock interviews with Senior Executives\r\n"
                     "  - Explore professional job opportunities\r\n"
                     "\r\n\n"
                     "We are excited to continue on this journey with you. Don't hesitate to email us at aspire@maxgala.com if you have any questions"
                     "\r\n\n"
                     "Best,\r\n"
                     "MAX Aspire Team"
                    )
        send_email(ADMIN_EMAIL, [user_email], SUBJECT, BODY_TEXT, None, CHARSET)
    elif user_type == 'PAID':
        BODY_TEXT = (f"Salaam {user_name}!\r\n"
                "\r\n\n"
                "Welcome to MAX Aspire, our community of high achieving individuals aspiring for success. You have taken the first step to grow your career and develop a long lasting network and set of skills."
                "On behalf of MAX Aspire, we welcome you and thank you for signing up.\r\n"
                "\r\n\n"
                "As an Aspiring Professional, here is how you can get started:\r\n"
                "  - Book coffee chats with Senior Executives\r\n"
                "  - Setup mock interviews with Senior Executives\r\n"
                "  - Explore professional job opportunities\r\n"
                "  - Post your resume for recruiters\r\n"
                "  - Connect with the job poster\r\n"
                "\r\n\n"
                "We are excited to continue on this journey with you. Don't hesitate to email us at aspire@maxgala.com if you have any questions"
                "\r\n\n"
                "Best,\r\n"
                "MAX Aspire Team"
            )
        send_email(ADMIN_EMAIL, [user_email], SUBJECT, BODY_TEXT, None, CHARSET)
    elif user_type == 'MENTOR':
        logger.info('disabling user of type {%s}' % (user_type))
        response = cognito_client.admin_disable_user(
            UserPoolId=event['userPoolId'],
            Username=event['userName']
        )
        logger.info(response)

        BODY_TEXT = (f"Salaam {user_name}!\r\n"
                     "\r\n\n"
                     "Thank you for signing up as a Senior Executive on MAX Aspire. "
                     "Our team is working on your request and will send over an update within 48 to 72 hours.\r\n"
                     "We really appreciate your time and commitment to helping our Aspiring Professionals. "
                     "Please don’t hesitate to reach out to aspire@maxgala.com if you have any questions.\r\n"
                     "\r\n\n"
                     "Best,\r\n"
                     "MAX Aspire Team"
                    )
        send_email(ADMIN_EMAIL, [user_email], SUBJECT, BODY_TEXT, None, CHARSET)
    else:
        # TODO: raise error (do not allow sign up)
        logger.info('invalid user_type: disabling user of type {%s}' % (user_type))
        response = cognito_client.admin_disable_user(
            UserPoolId=event['userPoolId'],
            Username=event['userName']
        )
        logger.info(response)

    return event
