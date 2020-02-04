import os
import base64
import csv
import datetime
import time
import json
import re
from pprint import pprint

from PyPDF4 import PdfFileReader, PdfFileWriter

from main import app
from core import action_hub, get_output_file_name, get_temp_file_name, get_sdk_for_schedule, get_sdk_all_access, send_email
from api_types import ActionDefinition, ActionList, ActionRequest, ActionForm, ActionFormField, FormSelectOption 

# TODO: Add ability to handle LookML dashboards
# TODO: Page size / height & width / pdf params: figure out the right approach
# TODO: Resolve option dropdowns on action form

DEFAULT_PDF_HEIGHT = int(1680 * 210 / 297)
DEFAULT_PDF_WIDTH = 1680
DEFAULT_PDF_PAGE_SIZE = 'A4'
DEFAULT_PDF_IS_LANDSCAPE = True

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
                supported_formats= ['json'],
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
            name='file_name',
            label='Report Pack Name',
            description='Filename for the generated PDF document',
            required=True,
        ),
        ActionFormField(
            name='default_size',
            label='Default Page Size',
            description='Default page size where not otherwise specified',
            default='A4',
            options=[
                FormSelectOption(name='A3', label='A3'),
                FormSelectOption(name='A4', label='A4'),
                FormSelectOption(name='Letter', label='Letter'),
            ]
        ),
        ActionFormField(
            name='default_orientation',
            label='Default Page Orientation',
            description='Default page orientation where not otherwise specified',
            default='landscape',
            options=[
                FormSelectOption(name='landscape', label='Landscape'),
                FormSelectOption(name='portrait', label='Portrait'),
            ]
        )
    ]

def merge_pdfs(paths, output):
    pdf_writer = PdfFileWriter()

    for path in paths:
        pdf_reader = PdfFileReader(path)
        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))

    with open(output, 'wb') as out:
        pdf_writer.write(out)

def download_dashboard(sdk, dashboard_id, file_name, size=DEFAULT_PDF_PAGE_SIZE, is_landscape=DEFAULT_PDF_IS_LANDSCAPE):
    task = sdk.create_dashboard_render_task(
        dashboard_id= dashboard_id,
        result_format= 'pdf',
        body= {
            'style': 'tiled',
            'filters': None,
        },
        height= DEFAULT_PDF_HEIGHT,
        width= DEFAULT_PDF_WIDTH,
        # pdf_paper_size= size,
        # pdf_landscape= is_landscape,
        # TODO: Parameterise PDF settings        
    )

    # poll the render task until it completes
    elapsed = 0.0
    delay = 0.5  # wait .5 seconds
    while True:
        poll = sdk.render_task(task.id)
        if poll.status == "failure":
            print(poll)
            break
        elif poll.status == "success":
            break

        time.sleep(delay)
        elapsed += delay
    print(f"Render task completed in {elapsed} seconds")

    result = sdk.render_task_results(task.id)
    with open(file_name, "wb") as f:
        f.write(result)

@app.post(f'/actions/{slug}/action')
def action(payload: ActionRequest):
    """Endpoint for the Compile Report Pack action."""
    sdk = get_sdk_for_schedule(payload.scheduled_plan.scheduled_plan_id)

    data = json.loads(payload.attachment.data)
    board_id = data[0]['board_id']

    report_pack = sdk.homepage(board_id)

    report_structure = []
    for id in report_pack.section_order[1:]:
        for section in report_pack.homepage_sections:
            if section.id == str(id):
                report_section = {
                  'title': section.title,
                  'cover': '',
                  'pages': []
                }
                page_sizes = []
                for match in re.findall(r'\[(.*?)\]', section.title):
                    param, value = match.split(':')
                    if param == 'cover':
                        report_section['cover'] = value
                    if param == 'size':
                        page_sizes = value.split(',')

                page_num = 0
                for item in section.homepage_items:
                    if item.dashboard_id:
                        page = {
                            'title': item.title,
                            'dashboard_id': item.dashboard_id,
                            'size': '',
                            'orientation': '',
                            'filters': []
                        }
                        if page_sizes:
                            page['size'] = page_sizes[page_num]
                            page['orientation'] = 'landscape'
                        report_section['pages'].append(page)
                        page_num += 1
                report_structure.append(report_section)

    pprint(report_structure)
    pdfs_to_merge = []
    for section in report_structure:
        if section['cover']:
            pdfs_to_merge.append(os.path.join('input', slug, section['cover']))
        for page in section['pages']:
            file_name = get_temp_file_name(slug, page['title'].replace(' ', '_')) + '.pdf'

            if 'size' in page.keys():
                if page['size']: 
                    page_size = page['size']
                else:
                    page_size = DEFAULT_PDF_PAGE_SIZE

            if 'orientation' in page.keys():
                if page['orientation'] == 'landscape':
                    page_is_landscape = True
                elif page['orientation'] == 'portrait':
                    page_is_landscape = False
                else:
                    page_is_landscape = DEFAULT_PDF_IS_LANDSCAPE

            print(f'Downloading: {file_name} Size: {page_size} Is Landscape: {page_is_landscape}')
            download_dashboard(sdk, page['dashboard_id'], file_name, page_size, page_is_landscape)
            pdfs_to_merge.append(file_name)

    report_pack_file = get_output_file_name(slug, report_pack.title) + '.pdf' # TODO: Use board title or form file_name?
    merge_pdfs(pdfs_to_merge, report_pack_file)

    pprint(pdfs_to_merge)

    response = send_email(
        to_emails= payload.form_params['email_address'],
        subject= payload.form_params['email_subject'],
        body= payload.form_params['email_body'],
        file_name= report_pack_file,
        file_type= 'pdf'
    )

    return {'response': 'response'}

