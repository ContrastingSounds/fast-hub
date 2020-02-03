import os
import traceback
import sys
import base64
from typing import Optional, Union, List
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI
import sendgrid
from sendgrid.helpers.mail import Mail, Email, Content, Attachment, FileContent, FileName, FileType, Disposition, ContentId

from looker_sdk import client, sdk


app = FastAPI(
    title='Fast Hub',
    description='Simple Python Action Hub for Looker, using the FastAPI library. Also uses SendGrid for emails.',
    version='0.1.0'
)

action_hub = os.environ.get('FAST_HUB', '127.0.0.1:8000')
sendgrid_from_email = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@example.com')
sendgrid_api_key = os.environ.get('SENDGRID_API_KEY', '')

if not os.path.exists('output'):
    os.makedirs('output')

if not os.path.exists('temp'):
    os.makedirs('temp')

def get_output_file_name(module: str, file_name: str, timestamp: bool = False, subfolder: str = '') -> str:
    if timestamp:
        timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d.%H:%M:%S')
        if len(file_name.split('.')) > 1:
            name_parts = file_name.split('.')[:-1]
            ext = file_name.split('.')[-1:]
            name_parts.append(timestamp)
            name_parts += ext
            file_name = '.'.join(name_parts)
        else:
            file_name = '.'.join([file_name, timestamp])

    if not os.path.exists(os.path.join('output', module)):
        os.makedirs(os.path.join('output', module))
    
    if subfolder:
        if not os.path.exists(os.path.join('output', module, subfolder)):
            os.makedirs(os.path.join('output', module, subfolder))
        output_file_name = os.path.join('output', module, subfolder, file_name)
    else:
        output_file_name = os.path.join('output', module, file_name)
    
    return output_file_name

def get_temp_file_name(module: str, file_name: Optional[str]) -> str:
    if not file_name:
        file_name = module 
    
    if not os.path.exists(os.path.join('temp', module)):
        os.makedirs(os.path.join('temp', module))

    uuid = str(uuid4())
    if len(file_name.split('.')) > 1:
        name_parts = file_name.split('.')[:-1]
        ext = file_name.split('.')[-1:]
        name_parts.append(uuid)
        name_parts += ext
        file_name = '.'.join(name_parts)
    else:
        file_name = '.'.join([file_name, uuid])
    
    return os.path.join('temp', module, file_name)

def get_temp_dir(module: str) -> str:
    if not os.path.exists(os.path.join('temp', module)):
        os.makedirs(os.path.join('temp', module))
    
    return os.path.join('temp', module)

def send_email(
    to_emails: Union[str, List[str]], 
    subject: str, 
    body: str = None, 
    file_name: str = None, 
    file_type: str = None, 
    template_id: str = None
):
    from_email = sendgrid_from_email
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
    elif file_type == 'pdf':
        file_type = 'application/pdf'

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

def get_sdk_for_schedule(scheduled_plan_id: int) -> sdk.methods.LookerSDK:
    sdk = client.setup()

    plan = sdk.scheduled_plan(scheduled_plan_id)
    sdk.login_user(plan.user_id)

    return sdk

def get_sdk_all_access() -> sdk.methods.LookerSDK:
    sdk = client.setup()

    return sdk