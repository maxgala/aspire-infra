
##### You need to have AWS Credentials configured. 
##### Visit: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ses-template.html and https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-personalized-email-api.html for more info.
##### Examples of working templates can be seen in the backend CreateJob and CreateJobApplications endpoints. 

####################################################
##### Use (uncomment) this code to CREATE an email template.
## TemplateName: Should be the name of the endpoint where this template is being used
## SubjectPart: Title of the email
## IMPORTANT! ANY VARIABLES NEED TO BE ENCLOSED IN DOUBLE BRACKETS {{ VAR }}

# import boto3

# # Create SES client
# ses = boto3.client('ses')

# response = ses.create_template(
#   Template = {
#     'TemplateName' : "CreateJob",
#     'SubjectPart'  : "[MAX Aspire] Your {{job_title}} job is under review",
#     'TextPart'     : "Salaam!\n\nThank you for choosing MAX Aspire as your entrusted partner. I am delighted to confirm that we have received your job posting {{job_title}} on {{today}}.\n\nYour Job Posting will be reviewed and if approved, will go LIVE within 36 hours.\n\nYou will be notified by email as individuals apply for the position.\n\nThank you.\n\nKind Regards,\nTeam MAX Aspire",
#   }
# )

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
