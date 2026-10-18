# Local validation

Completed October 18, 2026, with Python 3.13.7 on Windows.

| Check | Outcome |
| --- | --- |
| Analysis script | Completed; generated prepared data, reports, metrics, predictions and chart |
| Dataset tests | 2 passed: original-record reconciliation and duplicate-customer rejection |
| Notebook execution | 4 code cells executed in order; no error outputs |
| Notebook schema | nbformat validation passed |
| Original Power BI ZIP CRCs | Both passed; originals unchanged |
| Template candidate | CRC, model JSON, four parameterized paths, preserved layout checks passed |
| Chart visual review | Passed: readable labels and correct percentage axis |
| Git whitespace check | Passed |

The Windows sandbox prevented the duplicate-data test's temporary files and notebook kernel startup; both were successfully run with authorized unrestricted execution. No source data or results were changed to make tests pass.

Installed package versions are in reports/validation.json and requirements.txt. No fresh-environment installation or remote CI run was performed. Power BI Desktop open, refresh, DAX evaluation, visuals, interactions and moved-folder checks remain unverified; see powerbi/README.md. This status is not a claim of complete Power BI validation.
