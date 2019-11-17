from pydantic import BaseModel, Schema
from typing import List, Optional
from enum import Enum


class LookerInstance(BaseModel):
    name: str = None
    protocol: int = 9999
    api_port: int = 19999
    client_id: str = None
    client_secret: str = None


# https://github.com/looker/actions/blob/master/docs/action_api.md#action-form-endpoint

# Actions List Endpoint 

class Param(BaseModel):
    name: str
    label: str
    description: str = None
    required: bool = False
    sensitive: bool = False
    type: str = None


class RequiredField(BaseModel):
    tag: Optional[str]
    any_tag: Optional[List[str]]
    all_tags: Optional[List[str]]


class SupportedActionTypes(str, Enum):
    Cell = "cell"
    Query = "query"
    Dashboard = "dashboard"


class ActionSupportedDownloadSettings(str, Enum):
    Push = "push"
    Url = "url"


class ActionSupportedFormats(str, Enum):
    Txt = 'txt'
    Csv = 'csv'
    InlineJson = 'inline_json'
    Json = 'json'
    JsonDetail = 'json_detail'
    JsonDetailLiteStream = 'json_detail_lite_stream'
    Xlsx = 'xlsx'
    Html = 'html'
    WysiwygPdf = 'wysiwyg_pdf'
    AssembledPdf = 'assembled_pdf'
    WysiwygPng = 'wysiwyg_png'
    CsvZip = 'csv_zip'


class ActionSupportedFormattings(str, Enum):
    Formatted = 'formatted'
    Unformatted = 'unformatted'


class ActionSupportedVisualizationFormattings(str, Enum):
    Apply = 'apply'
    Noapply = 'noapply'


class ActionDefinition(BaseModel):
    name: str = ''
    url: str = ''
    label: str = ''
    icon_data_uri: str = ''
    form_url: str = ''
    supported_action_types: List[SupportedActionTypes] = []
    description: str = ''
    params: List[Param] = []
    supported_formats: List[ActionSupportedFormats] = []
    supported_formattings: List[ActionSupportedFormattings] = []
    supported_visualization_formattings: List[ActionSupportedVisualizationFormattings] = []
    # supported_download_settings: List[ActionSupportedDownloadSettings] = []
    required_fields: List[RequiredField] = []


class ActionList(BaseModel):
    integrations: List[ActionDefinition] = []


# Action Execute Endpoint

class ScheduledPlan(BaseModel):
    scheduled_plan_id: int
    title: str
    type: str
    url: str
    query_id: Optional[int]
    query: Optional[dict]
    filters_differ_from_look: Optional[str]
    download_url: Optional[str]


class Attachment(BaseModel):
    mimetype: str
    extension: str
    data: str


class ActionRequest(BaseModel):
    type: str
    scheduled_plan: ScheduledPlan 
    attachment: Attachment 
    data: dict
    form_params: dict


# Action Form Endpoint

class ActionState(BaseModel):
    data: Optional[str]
    refresh_time: Optional[int]


class FormSelectOption(BaseModel):
    name: str
    label: Optional[str]


class ActionFormField(BaseModel):
    name: str = ''
    label: Optional[str]
    description: Optional[str]
    type: Optional[str]
    required: Optional[bool]
    sensitive: Optional[bool]
    options: Optional[List[FormSelectOption]]


class ActionForm(BaseModel):
    action_form_fields: List[ActionFormField] = Schema(..., alias='fields')
    state: Optional[ActionState]
    # error: Union[Error, str]