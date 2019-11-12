import datetime

from docx import Document
from docx.shared import Inches
from fastapi import BackgroundTasks

from core import get_sdk_all_access, send_email
from main import app


def write_docx_from_folder(folder_id: int):
    sdk = get_sdk_all_access()
    folder = sdk.folder(folder_id)
    looks = folder.looks

    timestamp = datetime.datetime.now()

    document = Document()
    document.sections[0].header.paragraphs[0].text = folder.name
    document.sections[0].footer.paragraphs[0].text = f'Created {timestamp}'

    titles = []
    pages = len(looks) - 1

    for idx, look in enumerate(looks):
        image = sdk.run_look(look.id, 'png')
        image_file = f'temp/look{idx}.png'
        with open(image_file, 'wb') as file:
            file.write(image)
        document.add_heading(look.title, 0)
        document.add_paragraph(look.description)
        document.add_picture(image_file, width=Inches(5))
        if idx < pages:
            document.add_page_break()
    
    document.save(f'temp/folder{folder_id}.docx')


@app.get('/extensions/folder_to_word/folder/{folder_id}', status_code=202)
def endpoint(folder_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_docx_from_folder, folder_id)

    return {'message': 'Generating DOCS in background'}


@app.get('/extensions/folder_to_word/folders', status_code=200)
def folders():
    sdk = get_sdk_all_access()
    all_folders = sdk.all_folders()

    folders = []
    for folder in all_folders:
        if folder.name not in ['Shared', 'Users', 'lookml']:
            folders.append({
                folder.id: folder.name
            })

    return {'folders': folders}
