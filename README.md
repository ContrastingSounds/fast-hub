# fast-hub
Simple Looker Action Hub using Python + FastAPI. Includes SendGrid for emails.

# To use
Requites Python 3.6+. I haven't tested this for deployment yet. After cloning the repo, this might work for you, too:

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `./start`

# FastAPI – Automatic OpenAPI documentation

<img src="https://github.com/ContrastingSounds/fast-hub/blob/master/docs/images/open_api_docs.png" width="400">

# Adding a new action

Any new, conforming action added to the actions folder will automatically be added to the Action Hub.

- [ ] `from core import action_hub` _(imports the base url for the action hub)_
- [ ] `from core import` ... _any desired helper functions (e.g. to get sdk client, send emails, create temp files, ...)_
- [ ] `from main import app` _(imports the main application)_
- [ ] `from api_types import ActionDefinition, ActionList, ActionFormField, ActionRequest, ActionForm`
- [ ] `slug = (action slug)` _(code- and url- friendly name for the action)_
- [ ] `icon_uri = (data uri for icon image)` _(DATAURI GENERATOR: https://dopiaza.org/tools/datauri/index.php)_
- [ ] `definition = ActionDefinition()` _(This definition will be used to register the action)_
- [ ] `def form()` _(This form will be filled in by the user when sending/scheduling the action)_
- [ ] `def action()` _(The action itself)_
