import importlib.util
from pathlib import Path
import tempfile
import unittest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('analysis',ROOT/'analysis.py')
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)

class DataChecks(unittest.TestCase):
    def test_source_reconciliation(self):
        data,rejected,flags,audit = analysis.prepare()
        self.assertEqual(len(data['usage_monthly'])+len(rejected),audit['source_rows']['usage_monthly'])
        self.assertEqual(len(data['customers']),20000)
        self.assertEqual(data['customers'].Churned.sum(),3913)
        self.assertEqual(len(rejected),1)
        self.assertEqual(audit['surveys_after_exit'],470)

    def test_duplicate_customer_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ['customers','companies','survey','usage_monthly']:
                frame = pd.read_csv(ROOT/f'{name}.csv')
                if name=='customers':
                    frame = pd.concat([frame,frame.iloc[[0]]],ignore_index=True)
                frame.to_csv(root/f'{name}.csv',index=False)
            with self.assertRaisesRegex(ValueError,'duplicate full rows'):
                analysis.prepare(root)

if __name__=='__main__':
    unittest.main()
