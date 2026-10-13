#!/usr/bin/env python3
"""Publier les sources, deux branches et deux PR à partir de publication.json."""
import argparse
import ast
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]

def run(args, cwd, **kwargs):
    return subprocess.run(args, cwd=cwd, text=True, check=True, **kwargs)

def commit(repo, message):
    run(['git', 'add', '.'], repo)
    run(['git', 'commit', '-m', message], repo)

def write(repo, name, content):
    target = repo / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    if name.endswith('.sh'):
        target.chmod(0o755)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--merge', action='store_true', help='Fusionner après validation des tests, avec commits conservés.')
    args = parser.parse_args()
    state = json.loads((ROOT / 'publication.json').read_text())
    url = state['repository']
    slug = url[len('https://github.com/'):] if url.startswith('https://github.com/') else url
    if state.get('pull_requests'):
        parser.error('Des PR sont déjà enregistrées : vérifier leur état avant reprise.')
    # Ne jamais écraser une branche principale déjà publiée.
    refs = subprocess.run(['git', 'ls-remote', url], capture_output=True, text=True, check=True)
    if refs.stdout.strip():
        parser.error('Le dépôt distant contient déjà des références ; reprise manuelle nécessaire.')
    repo = Path(tempfile.mkdtemp(prefix='infra-modernisation-'))
    state['checkout'] = str(repo)
    (ROOT / 'publication.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    run(['git', 'init', '-b', 'main'], repo)
    # Réutiliser l’identité Git configurée ; demander de la configurer si absente.
    for key in ['user.name', 'user.email']:
        value = subprocess.run(['git', 'config', '--get', key], cwd=ROOT, capture_output=True, text=True)
        identity = value.stdout.strip()
        if not identity and key == 'user.name':
            identity = slug.split('/')[0]
        if not identity:
            parser.error('Configurer l’identité Git ' + key + ' avant publication.')
        run(['git', 'config', key, identity], repo)
    for name in ['README.md', 'project.json', '.gitignore']:
        shutil.copy2(ROOT / name, repo / name)
    shutil.copytree(ROOT / 'docs', repo / 'docs')
    shutil.copytree(ROOT / '.github', repo / '.github')
    (repo / 'scripts').mkdir()
    for name in ['publish-project.py', 'publish-interventions.py', 'configure-views.py', 'sync-status.py']:
        shutil.copy2(ROOT / 'scripts' / name, repo / 'scripts' / name)
    commit(repo, 'docs: initialiser le pilotage de la modernisation sur 12 semaines')
    run(['git', 'remote', 'add', 'origin', url], repo)
    run(['git', 'push', '-u', 'origin', 'main'], repo)
    test_source = (ROOT / 'tests/test_scripts.py').read_text()
    tree = ast.parse(test_source)
    header = test_source[:test_source.index('class DiskTests')]
    classes = {node.name: '\n'.join(test_source.splitlines()[node.lineno - 1:node.end_lineno]) + '\n'
               for node in tree.body if isinstance(node, ast.ClassDef)}
    prs = []
    for local_id, branch, name in [(11, 'feature/controle-disque', 'check-disk.sh'),
                                    (14, 'feature/sauvegarde-verifiee', 'backup.sh')]:
        issue = state['issues'][str(local_id)]['number']
        run(['git', 'switch', 'main'], repo)
        run(['git', 'switch', '-c', branch], repo)
        final = (ROOT / 'scripts' / name).read_text()
        if local_id == 11:
            first = '''#!/usr/bin/env bash
set -euo pipefail
threshold=${1:-80}
LC_ALL=C df -Pk | awk -v limit="$threshold" 'NR>1 {usage=$5; sub(/%$/, "", usage); if (usage+0 > limit) {print "ALERTE : " $0; alert=1}} END {exit alert ? 1 : 0}'
'''
            write(repo, 'scripts/' + name, first)
            commit(repo, f'feat: contrôler les seuils disque — Refs #{issue}')
            before_fix = final.replace('usage+0 >= limit', 'usage+0 > limit')
            write(repo, 'scripts/' + name, before_fix)
            partial_tests = classes['DiskTests'].replace("    def test_equal(self): self.assertEqual(self.run_disk(80).returncode, 1)\n", '').replace("    def test_leading_zero(self): self.assertEqual(self.run_disk(80, '080').returncode, 1)\n", '')
            write(repo, 'tests/test_disk.py', header + partial_tests)
            run(['python3', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], repo)
            commit(repo, f'test: valider les entrées et erreurs du contrôle disque — Refs #{issue}')
            write(repo, 'tests/test_disk.py', header + classes['DiskTests'])
            expected_failure = subprocess.run(['python3', '-m', 'unittest', 'discover', '-s', 'tests'], cwd=repo, capture_output=True, text=True)
            if expected_failure.returncode == 0:
                raise RuntimeError('Le défaut du seuil exact n’a pas été reproduit.')
            write(repo, 'scripts/' + name, final)
            run(['python3', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], repo)
            commit(repo, f'fix: alerter dès le seuil exact et accepter 080 — Refs #{issue}')
        else:
            first = '''#!/usr/bin/env bash
set -euo pipefail
(( $# == 2 )) || exit 2
mkdir -p -- "$2"
work=$(mktemp -d "$2/backup-XXXXXXXX")
tar -czf "$work/archive.tar.gz" -C "$1" .
printf 'Archive : %s\\n' "$work/archive.tar.gz"
'''
            write(repo, 'scripts/' + name, first)
            commit(repo, f'feat: archiver un répertoire de sauvegarde — Refs #{issue}')
            write(repo, 'scripts/' + name, final)
            write(repo, 'tests/test_backup.py', header + classes['BackupTests'])
            # Ne pas accepter une validation silencieusement ignorée.
            if not shutil.which('sha256sum'):
                raise RuntimeError('sha256sum requis pour valider la sauvegarde avant publication.')
            run(['python3', '-m', 'unittest', 'discover', '-s', 'tests', '-v'], repo)
            commit(repo, f'feat: vérifier l’intégrité et sécuriser la destination — Refs #{issue}')
        run(['bash', '-n', 'scripts/' + name], repo)
        run(['git', 'push', '-u', 'origin', branch], repo)
        body = (f"Livrer {name} avec validation automatisée.\n\n"
                + ('Le défaut du seuil exact a été reproduit puis corrigé ; six tests passent.\n' if local_id == 11 else 'Archivage, contrôle SHA-256 et restauration vérifiés ; destination imbriquée refusée.\n')
                + f'\nCloses #{issue}\n')
        body_file = repo / '.git' / ('pr-' + str(issue) + '.md')
        body_file.write_text(body)
        created = run(['gh', 'pr', 'create', '--repo', slug, '--base', 'main', '--head', branch,
                       '--title', 'Contrôle des seuils disque' if local_id == 11 else 'Sauvegarde avec contrôle d’intégrité',
                       '--body-file', str(body_file)], repo, capture_output=True)
        pr_url = created.stdout.strip()
        entry = {'issue': issue, 'url': pr_url, 'branch': branch}
        prs.append(entry)
        state['pull_requests'] = prs
        (ROOT / 'publication.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
        if args.merge:
            head = run(['git', 'rev-parse', 'HEAD'], repo, capture_output=True).stdout.strip()
            for attempt in range(30):
                checks = run(['gh', 'run', 'list', '--repo', slug, '--branch', branch, '--json', 'databaseId,headSha', '--limit', '10'], repo, capture_output=True)
                matching = [r for r in json.loads(checks.stdout) if r['headSha'] == head]
                if matching:
                    break
                time.sleep(2)
            else:
                raise RuntimeError('Workflow CI non démarré ; PR conservée sans fusion.')
            for check in matching:
                run(['gh', 'run', 'watch', str(check['databaseId']), '--repo', slug, '--exit-status', '--interval', '5'], repo)
            run(['gh', 'pr', 'merge', pr_url, '--merge'], repo)
            run(['git', 'switch', 'main'], repo)
            run(['git', 'pull', '--ff-only'], repo)
    print('PR créées :', json.dumps(prs, ensure_ascii=False))
    print('Clone conservé :', repo)

if __name__ == '__main__':
    main()
