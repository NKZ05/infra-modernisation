import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'

class PlanningTests(unittest.TestCase):
    def test_plan(self):
        import json
        plan = __import__('json').loads((SCRIPTS.parent / 'project.json').read_text())
        issues = plan['issues']; by_id = {x['id']: x for x in issues}
        milestones = {x['id']: x for x in plan['milestones']}
        self.assertEqual(len(issues), 16)
        self.assertEqual(sum(x['days'] for x in issues), 71)
        for x in issues:
            self.assertLessEqual(x['start'], x['end'])
            self.assertLessEqual(x['end'], milestones[x['milestone']]['due'])
            for dependency in x['dependencies']:
                self.assertLessEqual(by_id[dependency]['end'], x['start'])
