import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / 'skills' / 'data-detective' / 'scripts'
sys.path.insert(0, str(SCRIPT_DIR))
spec = importlib.util.spec_from_file_location('analyze', SCRIPT_DIR / 'analyze.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class EDATests(unittest.TestCase):
    def test_combined_sample(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'output'
            report = module.run(ROOT / 'examples/sample.csv', output)
            self.assertEqual(report['quality']['row_count'], 5)
            self.assertEqual(report['quality']['duplicate_row_count'], 1)
            self.assertTrue((output / 'report.md').is_file())
            self.assertTrue((output / 'report.json').is_file())
            self.assertTrue(report['eda']['charts'])
            self.assertTrue((output / report['eda']['charts'][0]).is_file())

    def test_chart_escapes_html(self):
        svg = module.make_svg_bars(['<script>alert(1)</script>'], [2], 'Unsafe <name>')
        self.assertNotIn('<script>', svg)
        self.assertIn('&lt;script&gt;', svg)

    def test_max_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertRaises(ValueError, module.run, ROOT / 'examples/sample.csv', Path(tmp), 5001)

if __name__ == '__main__':
    unittest.main()
