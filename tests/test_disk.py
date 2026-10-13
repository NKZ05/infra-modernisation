import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'

class DiskTests(unittest.TestCase):
    def run_disk(self, usage, threshold='80', failure=False):
        with tempfile.TemporaryDirectory() as tmp:
            stub = Path(tmp) / 'df'
            stub.write_text('#!/bin/sh\n' + ('exit 1\n' if failure else
                "printf '%s\\n' 'Filesystem 1024-blocks Used Available Capacity Mounted on' "
                f"'/dev/test 100 80 20 {usage}% /data with spaces'\n"))
            stub.chmod(0o755)
            return subprocess.run(['bash', str(SCRIPTS / 'check-disk.sh'), threshold],
                env=dict(os.environ, PATH=tmp + ':' + os.environ['PATH']), capture_output=True)
    def test_below(self): self.assertEqual(self.run_disk(79).returncode, 0)
    def test_full(self): self.assertEqual(self.run_disk(100).returncode, 1)
    def test_invalid(self): self.assertEqual(self.run_disk(80, '101').returncode, 2)
    def test_df_failure(self): self.assertEqual(self.run_disk(0, failure=True).returncode, 2)
