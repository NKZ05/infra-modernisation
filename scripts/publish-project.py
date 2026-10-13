#!/usr/bin/env python3
"""Créer les objets GitHub depuis le plan ; nécessite gh authentifié."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / 'publication.json'

def api(endpoint, payload=None):
    command = ['gh', 'api', endpoint]
    if payload is not None:
        command += ['--method', 'POST', '--input', '-']
    result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout) if result.stdout.strip() else None

def graphql(query, variables=None):
    result = api('graphql', {'query': query, 'variables': variables or {}})
    if result.get('errors'):
        raise RuntimeError(json.dumps(result['errors'], ensure_ascii=False))
    return result['data']

def save(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', required=True)
    args = parser.parse_args()
    if not shutil.which('gh'):
        parser.error('Installer GitHub CLI et s’authentifier avec le scope project.')
    if STATE_FILE.exists():
        parser.error('publication.json existe : vérifier la publication précédente avant toute reprise.')
    plan = json.loads((ROOT / 'project.json').read_text())
    user = api('user')
    if user['login'].lower() != args.owner.lower():
        parser.error('Le propriétaire doit être le compte utilisateur actuellement authentifié.')
    # Refus explicite des dépôts existants ; ne pas confondre une panne API avec un 404.
    check = subprocess.run(['gh', 'api', f'repos/{args.owner}/infra-modernisation'], capture_output=True, text=True)
    if check.returncode == 0:
        parser.error('Le dépôt existe déjà ; aucune modification effectuée.')
    if 'HTTP 404' not in check.stderr:
        raise RuntimeError(check.stderr)
    repo = api('user/repos', {'name': 'infra-modernisation', 'private': False,
                              'description': 'TP — Modernisation Infrastructure & Sécurité', 'auto_init': False})
    state = {'repository': repo['html_url'], 'milestones': {}, 'issues': {}, 'items': {}}
    save(state)
    endpoint = f"repos/{args.owner}/infra-modernisation"
    domains = list(dict.fromkeys(x['domain'] for x in plan['issues']))
    for domain in domains:
        api(endpoint + '/labels', {'name': domain, 'color': '0969da'})
    for m in plan['milestones']:
        milestone = api(endpoint + '/milestones', {'title': m['title'], 'due_on': m['due'] + 'T23:59:59Z'})
        state['milestones'][str(m['id'])] = milestone['number']; save(state)
    for x in plan['issues']:
        body = (f"## Travail attendu\n{x['description']}\n\n## Critères de validation\n- [ ] {x['acceptance']}\n\n"
                f"## Planification simulée S4\nCharge : {x['days']} jours-personnes.\n"
                f"Priorité : {x['priority']}. Risque : {x['risk']}. Statut : {x['status']}.\n"
                f"Dates : {x['start']} → {x['end']}.\n")
        issue = api(endpoint + '/issues', {'title': x['title'], 'body': body, 'labels': [x['domain']],
                                         'milestone': state['milestones'][str(x['milestone'])]})
        state['issues'][str(x['id'])] = {'number': issue['number'], 'node_id': issue['node_id'], 'url': issue['html_url']}
        save(state)
    # Ajouter les liens avec les vrais numéros, après création de toutes les issues.
    for x in plan['issues']:
        number = state['issues'][str(x['id'])]['number']
        if x['dependencies']:
            api(endpoint + f'/issues/{number}/comments', {'body': 'Dépend de : ' + ', '.join(
                '#' + str(state['issues'][str(d)]['number']) for d in x['dependencies'])})
        if x['status'] == 'Terminé':
            subprocess.run(['gh', 'api', '--method', 'PATCH', endpoint + f'/issues/{number}',
                            '-f', 'state=closed'], check=True, capture_output=True)
    project = graphql('mutation($owner:ID!,$title:String!){createProjectV2(input:{ownerId:$owner,title:$title}){projectV2{id number url}}}',
                      {'owner': user['node_id'], 'title': plan['title']})['createProjectV2']['projectV2']
    state['project'] = project; save(state)
    graphql('mutation($p:ID!,$r:ID!){linkProjectV2ToRepository(input:{projectId:$p,repositoryId:$r}){repository{id}}}',
            {'p': project['id'], 'r': repo['node_id']})
    graphql('mutation($p:ID!){updateProjectV2(input:{projectId:$p,public:true}){projectV2{id}}}', {'p': project['id']})
    fields = {}
    specifications = {
        'Priorité': ['Critique', 'Haute', 'Normale', 'Basse'],
        'Domaine technique': domains,
        'Risque': ['Élevé', 'Moyen', 'Faible'],
        'Avancement': ['À faire', 'En cours', 'Bloqué', 'Terminé'],
        'Charge estimée': 'NUMBER', 'Date de début': 'DATE', 'Date de fin prévue': 'DATE'}
    for name, spec in specifications.items():
        data = {'projectId': project['id'], 'name': name,
                'dataType': 'SINGLE_SELECT' if isinstance(spec, list) else spec}
        if isinstance(spec, list):
            data['singleSelectOptions'] = [{'name': v, 'color': 'GRAY', 'description': v} for v in spec]
        field = graphql('mutation($input:CreateProjectV2FieldInput!){createProjectV2Field(input:$input){projectV2Field{... on ProjectV2Field{id name} ... on ProjectV2SingleSelectField{id name options{id name}}}}}',
                        {'input': data})['createProjectV2Field']['projectV2Field']
        fields[name] = field
    state['fields'] = fields; save(state)
    for x in plan['issues']:
        item = graphql('mutation($p:ID!,$i:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$i}){item{id}}}',
                       {'p': project['id'], 'i': state['issues'][str(x['id'])]['node_id']})['addProjectV2ItemById']['item']['id']
        state['items'][str(x['id'])] = item; save(state)
        values = {'Priorité': x['priority'], 'Domaine technique': x['domain'], 'Risque': x['risk'],
                  'Avancement': x['status'], 'Charge estimée': x['days'], 'Date de début': x['start'], 'Date de fin prévue': x['end']}
        for name, value in values.items():
            field = fields[name]
            if 'options' in field:
                value = {'singleSelectOptionId': next(o['id'] for o in field['options'] if o['name'] == value)}
            else:
                value = {'number' if name == 'Charge estimée' else 'date': value}
            graphql('mutation($input:UpdateProjectV2ItemFieldValueInput!){updateProjectV2ItemFieldValue(input:$input){projectV2Item{id}}}',
                    {'input': {'projectId': project['id'], 'itemId': item, 'fieldId': field['id'], 'value': value}})
    print('Dépôt :', repo['html_url'])
    print('Project :', project['url'])
    print('Configurer ensuite les vues, Insights, workflows et PR selon docs/.')

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print('Publication interrompue :', error, file=sys.stderr)
        print('Consulter publication.json pour les objets déjà créés.', file=sys.stderr)
        sys.exit(1)
