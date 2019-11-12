import os
import traceback
import sys
import base64

from fastapi import FastAPI
import sendgrid
from sendgrid.helpers.mail import Mail, Email, Content, Attachment, FileContent, FileName, FileType, Disposition, ContentId

from looker_sdk import client


app = FastAPI()

action_hub = os.environ.get('FAST_HUB', '127.0.0.1:8000')
sendgrid_api_key = os.environ.get('SENDGRID_API_KEY', '')

def send_email(from_email, to_emails, subject, body=None, file_name=None, file_type=None, template_id=None):
    sg = sendgrid.SendGridAPIClient(sendgrid_api_key)
    content = Content(
        'text/plain',
        body
    )
    
    if file_type == 'xlsx':
        file_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif file_type == 'pptx':
        file_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    elif file_type == 'docx':
        file_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    mail = Mail(from_email, to_emails, subject, content) 

    if file_name:
        # encode binary file so it can be JSON serialised for SendGrid call
        with open(file_name, 'rb') as f:
            data = f.read()
            f.close()
        encoded = base64.b64encode(data).decode()

        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType(file_type)
        attachment.file_name = FileName(file_name)
        attachment.disposition = Disposition("attachment")
        attachment.content_id = ContentId("Example Content ID")

        mail.attachment = attachment

    if template_id:
        mail.template_id = template_id

    response = sg.send(mail) 

    return response

def get_sdk_for_schedule(scheduled_plan_id):
    sdk = client.setup()

    plan = sdk.scheduled_plan(scheduled_plan_id)
    sdk.login_user(plan.user_id)

    return sdk

def get_sdk_all_access():
    sdk = client.setup()

    return sdk