import base64
import csv
import datetime

from main import app
from core import action_hub, get_output_file_name, get_temp_file_name, get_sdk_for_schedule, get_sdk_all_access, send_email
from api_types import ActionDefinition, ActionList, ActionFormField, ActionRequest, ActionForm

slug = 'compile_report_pack'

icon_data_uri = ''

definition = ActionDefinition(
                name= slug,
                url= f'{action_hub}/actions/{slug}/action',
                label= 'Report Pack',
                icon_data_uri= icon_data_uri,
                form_url= f'{action_hub}/actions/{slug}/form',
                supported_action_types= ['query'],
                description= 'This action will compile a PDF Report Pack, given a correctly constructed board layout. See documentation for further details.',
                params= [],
                supported_formats= ['csv'],
                supported_formattings= ['unformatted'],
                supported_visualization_formattings= ['noapply'],
            )

@app.post(f'/actions/{slug}/form')
def form():
    """Standard Action Hub endpoint. Returns this action's sending/scheduling form as a JSON response."""
    return [
        ActionFormField(
            name='email_address',
            label='Email Address',
            description='Email address to send Report Pack in PDF format.',
            required=True,
        ),
        ActionFormField(
            name='email_subject',
            label='Subject',
            description='Email subject line',
            required=True,
        ),
        ActionFormField(
            name='email_body',
            label='Body',
            description='Email body text',
            required=True,
            type='textarea'
        ),
        ActionFormField(
            name='filename',
            label='Filename',
            description='Filename for the generated PDF document',
            required=True,
        ),
    ]

@app.post(f'/actions/{slug}/action')
def action(payload: ActionRequest):
    """Endpoint for the Compile Report Pack action."""
    sdk = get_sdk_for_schedule(payload.scheduled_plan.scheduled_plan_id)


    response = send_email(
        to_emails=payload.form_params['email_address'],
        subject=payload.form_params['email_subject'],
        body=payload.form_params['email_body'],
        # file_name=file_name,
        # file_type='docx'
    )

    return {'response': 'response'}

