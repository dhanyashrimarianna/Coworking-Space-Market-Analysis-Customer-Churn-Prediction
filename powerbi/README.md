# Power BI setup and validation

## Status

Original PBIX/PBIT files remain unchanged. Their ZIP CRC checks pass. The original PBIT exposes a model schema; the compressed PBIX model has not been independently decoded or refreshed. These are not PBIP source projects.

`Visuals_repaired_CANDIDATE.pbit` is a patched template awaiting **Power BI Desktop open, refresh, DAX evaluation, visual and interaction validation**. CRC/JSON checks do not establish those behaviors. Desktop was not found at its standard installation path; no GUI validation is claimed.

## Changes

- All four CSV queries use a required text parameter `DataFolder`. Set it to the generated `data/prepared` directory, without a trailing slash.
- CSV parsing uses UTF-8, quoted fields and explicit en-US conversion for ISO dates.
- Active filter path: companies (1) to customers (*) to survey (*) and usage_monthly (*). Survey's direct company link is removed and its customer link activated with single-direction filtering, avoiding parallel active paths.
- Churn Rate format is 0.00%; averages use two decimals. Measure names remain compatible.
- Original one-page report layout with 12 visual containers is preserved byte-for-byte. The summed team-size visual remains sensitive to flagged extremes. Existing visual design/saved selections are not certified.
- Stale SecurityBindings is omitted in the candidate. Readable M queries and schema are included. Rebuild with `python repair_powerbi.py`.

## Desktop checklist

1. Run `python analysis.py`; inspect reports/validation.json.
2. Open/import the candidate PBIT in Desktop. Set DataFolder to the absolute prepared-data folder. Apply local file credentials/privacy settings as required.
3. Refresh four tables. Clear all report/page/visual/slicer filters; saved original queries contain selections such as Spaces. Confirm 20,000 customers, 5 companies, 4,979 surveys, 268,743 usage rows.
4. Confirm total customers 20,000; churned 3,913; active status 16,087; recorded churn share 19.565%, displayed as 19.57%. Active status does not mean active today.
5. Use companies[Company] for shared provider slicers. Compare company and location selections with reports/churn_by_company.csv and reports/churn_by_location.csv. Check survey filtering against a customer-ID join in Python.
6. Inspect all visuals, tooltips and interactions. Review team-size extremes before presenting totals; distinguish recorded churn share from period churn. Do not assume currency.
7. Save a new PBIX, reopen and refresh. Move the project, update DataFolder only and refresh again. Record Desktop version, counts and screenshots before calling the dashboard fully validated.

If Desktop rejects the candidate package, open the original PBIT, create DataFolder as a required Text parameter, apply each named query in queries.pq through Advanced Editor, change relationships/formats as above and save a fresh PBIX. The original embedded binary model is not rewritten.

References: [Microsoft templates](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-templates), [model relationships](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand).
