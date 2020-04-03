import os
import base64
import csv
import datetime
import time
import json
import re
from pprint import pprint

from PyPDF4 import PdfFileReader, PdfFileWriter
from typing import cast
# from looker_sdk import methods
from main import app
from core import action_hub, get_input_file_name, get_output_file_name, get_temp_file_name, get_sdk_for_schedule, get_sdk_all_access, send_email
from api_types import ActionDefinition, ActionList, ActionRequest, ActionForm, ActionFormField, FormSelectOption 

# TODO: Add ability to handle LookML dashboards
# TODO: Page size / height & width / pdf params: figure out the right approach
# TODO: Resolve option dropdowns on action form

DEFAULT_PDF_HEIGHT = 986
DEFAULT_PDF_WIDTH = 1394
PDF_SIZES = {
    'A3': {
        'height': 1120,
        'width': 1584
    },
    'A4': {
        'height': 986,
        'width': 1394
    }
}
DEFAULT_PDF_PAGE_SIZE = 'A4'
DEFAULT_PDF_IS_LANDSCAPE = True
USE_SCALING = False

# DURING DEV ONLY
DOWNLOAD_DASHBOARDS = True
SEND_EMAIL = True

slug = 'compile_report_pack'

icon_data_uri = 'data:image/png;base64,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'

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
    """Form for the Compile Report Pack action: email details and pdf defaults (TBD)"""
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
        # ActionFormField(
        #     name='default_size',
        #     label='Default Page Size',
        #     description='Default page size where not otherwise specified',
        #     default='A4',
        #     options=[
        #         FormSelectOption(name='A3', label='A3'),
        #         FormSelectOption(name='A4', label='A4'),
        #         FormSelectOption(name='Letter', label='Letter'),
        #     ]
        # ),
        # ActionFormField(
        #     name='default_orientation',
        #     label='Default Page Orientation',
        #     description='Default page orientation where not otherwise specified',
        #     default='landscape',
        #     options=[
        #         FormSelectOption(name='landscape', label='Landscape'),
        #         FormSelectOption(name='portrait', label='Portrait'),
        #     ]
        # )
    ]

def merge_pdfs(paths, output):
    pdf_writer = PdfFileWriter()

    for path in paths:
        print(f'path {path[1]} {path[0]}')
        pdf_reader = PdfFileReader(path[0])
        for idx in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(idx)
            if USE_SCALING:
              if path[1] == 'A4':
                  print('scaling...')
                  page.scaleTo(812, 595) 
              else:
                  print('merge as is...')
            pdf_writer.addPage(page)

    with open(output, 'wb') as out:
        pdf_writer.write(out)

def get_filters(sdk, look_id):
    result = sdk.run_look(look_id, 'json')
    return json.loads(result)

# def download_dashboard(sdk: methods.LookerSDK , dashboard_id, file_name, size=DEFAULT_PDF_PAGE_SIZE, is_landscape=DEFAULT_PDF_IS_LANDSCAPE, filters=[]):
def download_dashboard(sdk, dashboard_id, file_name, size=DEFAULT_PDF_PAGE_SIZE, is_landscape=DEFAULT_PDF_IS_LANDSCAPE, filters=[]):
    if filters:
        filters = [f'{filter_[0]}={filter_[1]}' for filter_ in filters]
        filter_exp = '&'.join(filters)
    else:
        filter_exp = ''
    print(f'download_dashboard({dashboard_id}) with filter expression {filter_exp}')
    if DOWNLOAD_DASHBOARDS:
        try:
            height = PDF_SIZES[size]['height']
            width = PDF_SIZES[size]['width']
        except:
            print('FAILED to set height and width for PDF render')
            height = DEFAULT_PDF_HEIGHT
            width = DEFAULT_PDF_WIDTH        
        
        task = sdk.create_dashboard_render_task(
            dashboard_id= dashboard_id,
            result_format= 'pdf',
            body= {
                'dashboard_style': 'tiled',
                'dashboard_filters': filter_exp,
            },
            height= height,
            width= width,
            # pdf_paper_size= size,
            # pdf_landscape= is_landscape,    
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
                filters = []
                for item_id in section.item_order:
                    for item in section.homepage_items:
                        if item.id == str(item_id):
                            print('items loop, filters:', filters)
                            if item.look_id:
                                filters = get_filters(sdk, item.look_id)
                                pprint(filters)

                            if item.dashboard_id:
                                page = {
                                    'title': item.title,
                                    'dashboard_id': item.dashboard_id,
                                    'size': '',
                                    'orientation': '',
                                    'filters': filters
                                }
                                if page_sizes:
                                    page['size'] = page_sizes[page_num]
                                    page['orientation'] = 'landscape'
                                report_section['pages'].append(page)
                                page_num += 1
                                filters = []
                report_structure.append(report_section)

    print('Report Structure:')
    pprint(report_structure)

    pdfs_to_merge = []
    for section in report_structure:
        if section['cover']:
            cover_page = get_input_file_name(slug, section['cover'])
            pdfs_to_merge.append((cover_page, 'A4'))
        for page in section['pages']:
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

            if page['filters']:
                dashboard_filters = sdk.dashboard(page['dashboard_id']).dashboard_filters
                filter_map = {}
                for filter_ in dashboard_filters:
                    filter_map[filter_.dimension] = filter_.name

                for idx, filter_set in enumerate(page['filters']):
                    print(f'idx filter_set {idx} {filter_set}')
                    filters = []
                    for dimension, value in filter_set.items():
                        filters.append((filter_map[dimension], value))
                    file_name = get_temp_file_name(slug, page['title'].replace(' ', '_')) + f'_{idx}.pdf'
                    print(f'Downloading: {file_name} Size: {page_size} Is Landscape: {page_is_landscape}')
                    download_dashboard(sdk, page['dashboard_id'], file_name, page_size, page_is_landscape, filters)
                    pdfs_to_merge.append((file_name, page_size))
            else:
                file_name = get_temp_file_name(slug, page['title'].replace(' ', '_')) + '.pdf'
                print(f'Downloading: {file_name} Size: {page_size} Is Landscape: {page_is_landscape}')
                download_dashboard(sdk, page['dashboard_id'], file_name, page_size, page_is_landscape)
                pdfs_to_merge.append((file_name, page_size))


    report_pack_file = get_output_file_name(slug, cast(str, report_pack.title)) + '.pdf' # TODO: Use board title or form file_name?
    if DOWNLOAD_DASHBOARDS:
        merge_pdfs(pdfs_to_merge, report_pack_file) 
    pprint(pdfs_to_merge)

    if SEND_EMAIL:
        response = send_email(
            to_emails= payload.form_params['email_address'],
            subject= payload.form_params['email_subject'],
            body= payload.form_params['email_body'],
            file_name= report_pack_file,
            file_type= 'pdf'
        )

    return {'response': 'response'}

