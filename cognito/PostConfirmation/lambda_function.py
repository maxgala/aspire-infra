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
    logger.info(event)
    logger.info(context)
    if event['triggerSource'] == 'PostConfirmation_ConfirmForgotPassword':
        return event

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
                     "Congratulations for successfully signing up on MAX Aspire! We are thrilled to have you on board and can’t wait to make a positive difference in your professional career."
                     "At MAX, we are devoted to elevating the Muslim brand by serving aspiring professionals, such as yourself! The Aspire platform aims to bring together a powerful network to collaborate for a more rewarding career journey and help Muslims fulfill their true potential. More than 200 Senior Executives, including CEOs, Partners, Managing Directors and VPs, are already on board! You are now a part of this circle too!\r\n"
                     "\r\n\n"
                     "Check out the cool features we currently offer:\r\n"
                     "1. Resume Bank\r\n"
                     "2. Exclusive Coffee Chats\r\n"
                     "3. Hire MAX Professional Talent\r\n"
                     "4. Mock Interviews\r\n"
                     "\r\n\n"
                     "We sincerely hope you make the most of these services and help spread the word. As the Prophet said: 'Every Act of goodness is charity.' (Sahih Muslim, Hadith 496)\r\n"
                     "You can now access your account at https://aspire.maxgala.com\r\n"
                     "Should you need any assistance or have any questions or comments about your membership or benefits, please feel free to contact us at aspire@maxgala.com\r\n"
                     "\r\n\n"
                     "Sincerely,\r\n"
                     "Aazar Zafar\r\n"
                     "Founder and Head Cheerleader\r\n"
                     "MAX Aspire"
                    )
        send_email(ADMIN_EMAIL, [user_email], SUBJECT, BODY_TEXT, None, CHARSET)
    elif user_type == 'PAID':
        BODY_TEXT = (f"Salaam {user_name}!\r\n"
                     "\r\n\n"
                     "Congratulations for successfully signing up on MAX Aspire! We are thrilled to have you on board and can’t wait to make a positive difference in your professional career."
                     "At MAX, we are devoted to elevating the Muslim brand by serving aspiring professionals, such as yourself! The Aspire platform aims to bring together a powerful network to collaborate for a more rewarding career journey and help Muslims fulfill their true potential. More than 200 Senior Executives, including CEOs, Partners, Managing Directors and VPs, are already on board! You are now a part of this circle too!\r\n"
                     "\r\n\n"
                     "Check out the cool features we currently offer:\r\n"
                     "1. Resume Bank\r\n"
                     "2. Exclusive Coffee Chats\r\n"
                     "3. Hire MAX Professional Talent\r\n"
                     "4. Mock Interviews\r\n"
                     "\r\n\n"
                     "We sincerely hope you make the most of these services and help spread the word. As the Prophet said: 'Every Act of goodness is charity.' (Sahih Muslim, Hadith 496)\r\n"
                     "You can now access your account at https://aspire.maxgala.com\r\n"
                     "Should you need any assistance or have any questions or comments about your membership or benefits, please feel free to contact us at aspire@maxgala.com\r\n"
                     "\r\n\n"
                     "Sincerely,\r\n"
                     "Aazar Zafar\r\n"
                     "Founder and Head Cheerleader\r\n"
                     "MAX Aspire"
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
