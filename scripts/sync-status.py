#!/usr/bin/env python3
"""Utiliser le statut natif pour l’avancement et synchroniser les issues fermées."""
import json
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location('publisher', ROOT / 'scripts/publish-project.py')
api = module_from_spec(spec); spec.loader.exec_module(api)
state = json.loads((ROOT / 'publication.json').read_text())
plan = json.loads((ROOT / 'project.json').read_text())
pid = state['project']['id']
fields = api.graphql('query($p:ID!){node(id:$p){... on ProjectV2{fields(first:30){nodes{... on ProjectV2SingleSelectField{id name options{id name}}}}}}}', {'p': pid})['node']['fields']['nodes']
status = next((x for x in fields if x.get('name') == 'Status'), None)
if status:
    status = api.graphql('mutation($input:UpdateProjectV2FieldInput!){updateProjectV2Field(input:$input){projectV2Field{... on ProjectV2SingleSelectField{id name options{id name}}}}}',
        {'input': {'fieldId': status['id'], 'singleSelectOptions': [
            {'name': n, 'color': c, 'description': n} for n,c in [('À faire','GRAY'),('En cours','YELLOW'),('Bloqué','RED'),('Terminé','GREEN')]]}})['updateProjectV2Field']['projectV2Field']
else:
    status = state['fields']['Avancement']
slug = state['repository'].split('github.com/', 1)[1]
for x in plan['issues']:
    issue = api.api(slug and 'repos/' + slug + '/issues/' + str(state['issues'][str(x['id'])]['number']))
    value = 'Terminé' if issue['state'] == 'closed' else x['status']
    api.graphql('mutation($input:UpdateProjectV2ItemFieldValueInput!){updateProjectV2ItemFieldValue(input:$input){projectV2Item{id}}}',
        {'input': {'projectId': pid, 'itemId': state['items'][str(x['id'])], 'fieldId': status['id'],
                   'value': {'singleSelectOptionId': next(o['id'] for o in status['options'] if o['name'] == value)}}})
if status['name'] == 'Status':
    old = state['fields']['Avancement']
    api.graphql('mutation($f:ID!){deleteProjectV2Field(input:{fieldId:$f}){clientMutationId}}', {'f': old['id']})
    api.graphql('mutation($f:ID!){updateProjectV2Field(input:{fieldId:$f,name:"Avancement"}){projectV2Field{... on ProjectV2SingleSelectField{id name}}}}', {'f': status['id']})
    status['name'] = 'Avancement'
state['fields']['Avancement'] = status
api.save(state)
print('Avancement natif synchronisé avec les issues.')
