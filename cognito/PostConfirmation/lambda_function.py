import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cognito_client = boto3.client('cognito-idp')
ses_client = boto3.client('ses')

ADMIN_EMAIL = "saiima.ali@mail.utoronto.ca"
SUPPORT_EMAIL = "saleh.bakhit@hotmail.com"

CHARSET = "UTF-8"
SUBJECT = "MAX Aspire - Thank you for signing up"

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
        BODY_TEXT = ("Salaam!\r\n"
                     "\r\n"
                     "On behalf of MAX Aspire, we welcome you and thank you for signing up.\r\n"
                     "\r\n"
                     "You now have access to:\r\n"
                     "  - Viewing Job postings\r\n"
                     "  - Posting your Resume in Jobs Bank\r\n"
                     "  - Using pay-per-use service to connect with Senior Executives\r\n"
                     "\r\n"
                     "Refer a friend to signup for premium or platinum subscription and earn 10 credits! (?)\r\n"
                     "We are excited, once again, to welcome you. Please don’t hesitate to reach out to {support_email} if you have any questions.\r\n"
                     "\r\n"
                     "Best,\r\n"
                     "MAX Aspire Team"
                    )
        send_email(ADMIN_EMAIL, [user_email], SUBJECT, BODY_TEXT, None, CHARSET)
    elif user_type == 'PAID':
        BODY_TEXT = ("Salaam!\r\n"
                     "\r\n"
                     "On behalf of MAX Aspire, we welcome you and thank you for signing up.\r\n"
                     "\r\n"
                     "You now have access to:\r\n"
                     "  - Viewing and applying to Job postings\r\n"
                     "  - Access to connect with Job poster (?)\r\n"
                     "  - Posting your Resume in Jobs Bank\r\n"
                     "  - Posting Jobs\r\n"
                     "  - Using your credits to connect with Senior Executives\r\n"
                     "  - Board of Directors roles\r\n"
                     "\r\n"
                     "Refer a friend to signup for premium or platinum subscription and earn 10 credits! (?)\r\n"
                     "We are excited, once again, to welcome you. Please don’t hesitate to reach out to {support_email} if you have any questions.\r\n"
                     "\r\n"
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

        BODY_TEXT = ("Salaam!\r\n"
                     "\r\n"
                     "Thank you for signing up as a Senior Executive on MAX Aspire. "
                     "Our team is working on your request and will send over an update within 48 to 72 hours.\r\n"
                     "We really appreciate your time and commitment to helping our Aspiring Professionals. "
                     "Please don’t hesitate to reach out to {support_email} if you have any questions.\r\n"
                     "\r\n"
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

    logger.info('adding user to group')
    response = cognito_client.admin_add_user_to_group(
        UserPoolId=event['userPoolId'],
        Username=event['userName'],
        GroupName=user_type
    )
    logger.info(response)

    # user_type is being used
    # logger.info('deleing custom:user_type attribute')
    # response = cognito_client.admin_delete_user_attributes(
    #     UserPoolId=event['userPoolId'],
    #     Username=event['userName'],
    #     UserAttributeNames=[
    #         'custom:user_type'
    #     ]
    # )
    # logger.info(response)

    return event
