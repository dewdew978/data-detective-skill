import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/data-detective/scripts/audit_csv.py'
spec = importlib.util.spec_from_file_location('audit_csv', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class AuditTests(unittest.TestCase):
    def test_sample(self):
        data = module.audit(Path(__file__).resolve().parents[1] / 'examples/sample.csv')
        self.assertEqual(data['row_count'], 5)
        self.assertEqual(data['duplicate_row_count'], 1)
        age = next(c for c in data['columns'] if c['name'] == 'age')
        self.assertEqual(age['missing_count'], 2)
        self.assertTrue(age['potential_mixed_types'])

    def test_malformed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'rows.csv'
            path.write_text('a,b\n1,2\n3\n', encoding='utf-8')
            data = module.audit(path)
            self.assertEqual(data['malformed_row_count'], 1)
            self.assertEqual(data['malformed_rows'][0]['line'], 3)

if __name__ == '__main__':
    unittest.main()
