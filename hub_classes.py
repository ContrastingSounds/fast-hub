from pydantic import BaseModel
from typing import List


class LookerInstance(BaseModel):
    name: str = None
    protocol: int = 9999
    api_port: int = 19999
    client_id: str = None
    client_secret: str = None


class ScheduledPlan(BaseModel):
    scheduled_plan_id: int
    title: str
    type: str
    url: str
    query_id: int = None
    query: dict = None
    filters_differ_from_look: str = None
    download_url: str = None


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


class ActionPayload(BaseModel):
    body: dict = None
    content_type: str = None
    content_id: int = None
    instance_name: str = None
    url: str = None
    url_with_params: str = None
    attachment_base64: str = None
    attachment_mimetype: str = None
    attachment_extension: str = None


class ActionParameter(BaseModel):
    name: str
    label: str
    description: str = None
    required: bool = False
    sensitive: bool = False
    type: str = None


class ActionDefinition(BaseModel):
    name: str = ''
    url: str = ''
    label: str = ''
    icon_data_uri: str = ''
    form_url: str = ''
    supported_action_types: List[str] = []
    description: str = ''
    params: List[ActionParameter] = []
    supported_formats: List[str] = []
    supported_formattings: List[str] = []
    supported_visualization_formattings: List[str] = []
    required_fields: List[str] = []


class ActionList(BaseModel):
    integrations: List[ActionDefinition] = []


class ActionFormParameter(BaseModel):
    name: str = ''
    label: str = ''
    description: str = ''
    required: bool = False
    sensitive: bool = False
    type: str = ''
    option: List[dict] = []


class ActionForm(BaseModel):
    params: List[ActionParameter] = []