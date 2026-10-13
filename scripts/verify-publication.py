#!/usr/bin/env python3
import collections
import datetime
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location('publisher', ROOT/'scripts/publish-project.py')
api=module_from_spec(spec);spec.loader.exec_module(api)
state=json.loads((ROOT/'publication.json').read_text())
slug=state['repository'].split('github.com/',1)[1]
project=api.graphql('query($p:ID!){node(id:$p){... on ProjectV2{public title views(first:20){nodes{name layout filter groupByFields(first:10){nodes{... on ProjectV2Field{name} ... on ProjectV2SingleSelectField{name}}}}} workflows(first:20){nodes{name enabled}} items(first:100){nodes{id content{... on Issue{number state}} fieldValues(first:30){nodes{... on ProjectV2ItemFieldNumberValue{number field{... on ProjectV2Field{name}}} ... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2SingleSelectField{name}}} ... on ProjectV2ItemFieldDateValue{date field{... on ProjectV2Field{name}}}}}}}}}}',{'p':state['project']['id']})['node']
charges=collections.Counter();statuses=collections.Counter()
for item in project['items']['nodes']:
    values={v['field']['name']: v.get('number',v.get('date',v.get('name'))) for v in item['fieldValues']['nodes'] if v}
    assert len(values)==8, values
    assert values['Status']==values['Avancement'], values
    charges[values['Domaine technique']]+=values['Charge estimée']
    statuses[values['Avancement']]+=1
assert sum(charges.values())==71
assert dict(statuses)=={'Terminé':8,'Bloqué':1,'En cours':3,'À faire':4},statuses
proof={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'repository':state['repository'], 'project':state['project']['url'], 'charges':dict(charges),'statuses':dict(statuses),'views':project['views']['nodes'],'workflows':project['workflows']['nodes'],'pull_requests':[]}
for entry in state['pull_requests']:
    number=int(entry['url'].rsplit('/',1)[1])
    pr=api.api(f'repos/{slug}/pulls/{number}')
    issue=api.api(f"repos/{slug}/issues/{entry['issue']}")
    assert pr['merged'] and issue['state']=='closed'
    commits=api.api(f'repos/{slug}/pulls/{number}/commits')
    assert len(commits)==(3 if entry['issue']==11 else 2)
    comment='## Traçabilité de l’intervention validée\n\nPR fusionnée : '+entry['url']+'\n\n'
    comment+='\n'.join('- ['+c['sha'][:7]+']('+c['html_url']+') — '+c['commit']['message'].splitlines()[0] for c in commits)
    comment+='\n\nTests locaux et workflow GitHub Actions validés avant fusion. Statut Project : Terminé. Cette validation technique succède à la photographie S4.'
    existing=api.api(f"repos/{slug}/issues/{entry['issue']}/comments")
    if not any(c['body']==comment for c in existing):
        api.api(f"repos/{slug}/issues/{entry['issue']}/comments",{'body':comment})
    proof['pull_requests'].append({'url':entry['url'],'merged':pr['merged'],'issue':entry['issue'],'issue_state':issue['state'],'commits':[{'sha':c['sha'],'url':c['html_url'],'message':c['commit']['message']} for c in commits]})
(ROOT/'docs/verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'charges':dict(charges),'statuses':dict(statuses),'views':proof['views']},ensure_ascii=False,indent=2))
