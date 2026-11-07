import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/data-detective/scripts'))
from analyze import run

class FindingsTests(unittest.TestCase):
    def test_findings_use_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            report = run(ROOT / 'examples/sample.csv', Path(temp), charts=False)
            codes = {f['code'] for f in report['findings']}
            self.assertIn('exact_duplicates', codes)
            self.assertIn('missing_values', codes)
            self.assertTrue(all('evidence' in f for f in report['findings']))
            self.assertIn('Questions to confirm', (Path(temp) / 'report.md').read_text())

    def test_refuse_to_overwrite_input(self):
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp) / 'report.md'
            src.write_text('a,b\n1,2\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'overwrite input'):
                run(src, Path(temp))
            self.assertEqual(src.read_text(), 'a,b\n1,2\n')

if __name__ == '__main__':
    unittest.main()
