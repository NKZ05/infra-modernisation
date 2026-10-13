import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'

class BackupTests(unittest.TestCase):
    def test_restore_and_checksum(self):
        import shutil
        if not shutil.which('sha256sum'):
            self.skipTest('sha256sum absent : test à exécuter sous Linux')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source'; source.mkdir()
            (source / 'document.txt').write_text('données du TP\n')
            destination = root / 'destination'
            result = subprocess.run(['bash', str(SCRIPTS / 'backup.sh'), str(source), str(destination)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            backup = next(destination.iterdir())
            subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=backup, check=True, capture_output=True)
            restore = root / 'restore'; restore.mkdir()
            subprocess.run(['tar', '-xzf', str(backup / 'archive.tar.gz'), '-C', str(restore)], check=True)
            self.assertEqual((restore / 'document.txt').read_bytes(), (source / 'document.txt').read_bytes())
            result = subprocess.run(['bash', str(SCRIPTS / 'backup.sh'), str(source), str(source / 'nested')], capture_output=True)
            self.assertEqual(result.returncode, 2)
