#!/usr/bin/env python3
"""Créer les vues via l’API ; regroupements et Insights restent dans l’interface."""
import json
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location('publisher', ROOT / 'scripts/publish-project.py')
api = module_from_spec(spec)
spec.loader.exec_module(api)
state = json.loads((ROOT / 'publication.json').read_text())
project = state['project']
fields = state['fields']
result = api.graphql('query($p:ID!){node(id:$p){... on ProjectV2{fields(first:30){nodes{... on ProjectV2Field{id name} ... on ProjectV2SingleSelectField{id name options{id name}}}} views(first:20){nodes{id name number}}}}}', {'p': project['id']})['node']
native = {x['name']: x for x in result['fields']['nodes']}
existing = {x['name']: x for x in result['views']['nodes']}
visible = [native['Title']['id']] + [fields[x]['id'] for x in ['Avancement', 'Priorité', 'Domaine technique', 'Charge estimée', 'Risque', 'Date de début', 'Date de fin prévue']] + [native['Milestone']['id']]
views = [
    ('Tableau opérationnel', 'BOARD_LAYOUT', ''),
    ('Suivi des charges', 'TABLE_LAYOUT', ''),
    ('Roadmap', 'ROADMAP_LAYOUT', ''),
    ('Synthèse de direction', 'TABLE_LAYOUT', 'is:open'),
    ('Risques élevés', 'TABLE_LAYOUT', 'is:open Risque:Élevé'),
    ('Charge globale', 'TABLE_LAYOUT', ''),
]
state['views'] = {}
for name, layout, filter_value in views:
    view = existing.get(name)
    if not view:
        view = api.graphql('mutation($input:CreateProjectV2ViewInput!){createProjectV2View(input:$input){projectV2View{id name number}}}',
                           {'input': {'projectId': project['id'], 'name': name, 'layout': layout,
                                      'configuration': {'visibleFieldIds': visible}}})['createProjectV2View']['projectV2View']
    if filter_value:
        api.graphql('mutation($input:UpdateProjectV2ViewInput!){updateProjectV2View(input:$input){projectV2View{id}}}',
                    {'input': {'viewId': view['id'], 'filter': filter_value}})
    state['views'][name] = dict(view, url=project['url'] + '/views/' + str(view['number']))
    api.save(state)
print(json.dumps(state['views'], ensure_ascii=False, indent=2))
