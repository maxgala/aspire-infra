
##### You need to have AWS Credentials configured. 
##### Visit: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ses-template.html and https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-personalized-email-api.html for more info.
##### Examples of working templates can be seen in the backend CreateJob and CreateJobApplications endpoints. 

####################################################
##### Use (uncomment) this code to CREATE an email template.
## TemplateName: Should be the name of the endpoint where this template is being used
## SubjectPart: Title of the email
## IMPORTANT! ANY VARIABLES NEED TO BE ENCLOSED IN DOUBLE BRACKETS {{ VAR }}

import boto3

# # Create SES client
ses = boto3.client('ses')

response = ses.create_template(
  Template = {
    'TemplateName' : "Connection-Initiation-SEtoSE",
    'SubjectPart'  : "[MAX Aspire] Someone wants to connect with you!",
    'TextPart'     : "Salaam {{requestee_name}}!\n\n{{requestor_name}}, a Senior Executive at MAX Aspire, has sent you a connection request.\n\nTo accept or reject this request, follow the steps listed below:\n1. Log in to your MAX Aspire account\n2. Under Community > Show Members\n3. Search for the name '{{requestor_name}}`\n\nFor more information, please visit https://aspire.maxgala.com or contact us at aspire@maxgala.com.\n\nBest regards,\nTeam MAX Aspire\n",
  }
)

response = ses.create_template(
  Template = {
    'TemplateName' : "Connection-Confirmation-SEtoSE",
    'SubjectPart'  : "[MAX Aspire] Your request has been accepted!",
    'TextPart'     : "Salaam {{requestor_name}}!\n\nCongratulations! {{requestoe_name}} has accepted your connection request.\n\nYou can now directly communicate with {{requestee_name}}. Please use the email address provided above.\n\nFor more information, please visit https://aspire.maxgala.com or contact us at aspire@maxgala.com.\n\nBest regards,\nTeam MAX Aspire\n",
  }
)

response = ses.create_template(
  Template = {
    'TemplateName' : "Connection-Initiation-SEtoAP",
    'SubjectPart'  : "[MAX Aspire] Someone likes your resume!",
    'TextPart'     : "Salaam {{requestee_name}}!\n\n{{requestor_name}} liked your resume and wants to connect with you!\n\nMAX Aspire is helping build a stronger and connected community. Thank you for your commitment and contributions towards the community.\n\nBest regards,\nTeam MAX Aspire\n",
  }
)

response = ses.create_template(
  Template = {
    'TemplateName' : "Job-Creation",
    'SubjectPart'  : "[MAX Aspire] Your {{job_title}} job is under review",
    'TextPart'     : "Salaam!\n\nThank you for choosing MAX Aspire as your entrusted partner. We are delighted to confirm that we have received your job posting {{job_title}} on {{today}}.\n\nYour Job Posting will be reviewed and if approved, will go LIVE within 2 business days.\n\nYou will be notified by email as individuals apply for the position.\n\nFor more information, please visit https://aspire.maxgala.com or contact us at aspire@maxgala.com.\n\nThank you.\n\nKind Regards,\nTeam MAX Aspire",
  }
)

response = ses.create_template(
  Template = {
    'TemplateName' : "JobApplication-Creation-HiringManager",
    'SubjectPart'  : "[MAX Aspire] {{candidate_name}} applied to your {{job_title}} job!",
    'TextPart'     : "Salaam!\n\nWe would like to notify that {{candidate_name}} has applied to the job posting {{job_title}} on {{today}}.\n\nKindly login to your account to access the application of the candidate under 'Jobs / View Submissions'. If you are interested in the candidate, please feel free to directly reach out to the individual.\n\nOver time, MAX Aspire will add new functionality to the 'View Submissions' section. We hope you come across stellar candidates in your review.\n\nBest regards,\nTeam MAX Aspire",
  }
)

response = ses.create_template(
  Template = {
    'TemplateName' : "JobApplication-Creation-Applicant",
    'SubjectPart'  : "[MAX Aspire] You have submitted a job application",
    'TextPart'     : "Salaam!\n\nThank you for choosing MAX Aspire as your entrusted partner. I am delighted to confirm that we have submitted your job application for the position of {{job_title}} on {{today}}.\n\nThe hiring manager has also been notified. If your application meets the requirement, you will be contacted with the next steps.\n\nFor more information, please visit https://aspire.maxgala.com or contact us at aspire@maxgala.com.\n\nGood luck and thank you.\n\nKind Regards,\nTeam MAX Aspire",
  }
)

response = ses.create_template(
  Template = {
    'TemplateName' : "Chat-Reservation",
    'SubjectPart'  : "[MAX Aspire] Coffee Connect Scheduling",
    'TextPart'     : "Salaam {mentee_name}!\n\nWe are delighted to confirm your {chat_type} with {mentor_name}, one of our many accomplished MAX Aspire Senior Executives!\n\nFollow the steps below to book a {chat_type} with {mentor_name}:\n\n1. As the initiating Aspiring Professional, reach out to the Senior Executive at {mentor_email} to determine a mutually convenient time to connect.\n2. Once a time has been agreed upon, set up a Zoom or Google Meet bridge and invite the Senior Executive on the email address provided.\n\nPlease ensure your punctuality and professionalism as this could be the beginning of a special journey.\n\n{mentor_name}, please note you have been cc’d to verify this is a MAX Aspire initiated connection. No action required.\n\nFor more information, please visit https://aspire.maxgala.com or contact us at aspire@maxgala.com.\n\nKind regards,\nThe MAX Aspire Team",
  }
)

# print(response)

####################################################
##### Use (uncomment) this code to list all the templates currently 

# import boto3

# Create SES client
# ses = boto3.client('ses')

# response = ses.list_templates(
#   MaxItems=10
# )
# print(response)

####################################################
##### Use (uncomment) this code to delete the template by referring to it's TemplateName 

# import boto3

# Create SES client
# ses = boto3.client('ses')
# response = ses.delete_template(
#     TemplateName='CreateJob2'
# )

# print(response)
