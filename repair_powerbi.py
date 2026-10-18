"""Build an inspectable template candidate. Desktop validation is still required."""
from pathlib import Path
import json
import re
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent

def build():
    out = ROOT/'powerbi'
    out.mkdir(exist_ok=True)
    with zipfile.ZipFile(ROOT/'Visuals.pbit') as original:
        assert original.testzip() is None
        schema = json.loads(original.read('DataModelSchema').decode('utf-16-le'))
        model = schema['model']
        model['expressions'] = [{'name':'DataFolder','kind':'m',
            'expression':'"C:\\CHANGE_ME\\data\\prepared" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]',
            'annotations':[{'name':'PBI_ResultType','value':'Text'}]}]
        queries = []
        for table in model['tables']:
            for partition in table.get('partitions',[]):
                source = partition['source']
                if source['type'] != 'm':
                    continue
                expression = '\n'.join(source['expression'])
                expression, count = re.subn(r'File\.Contents\("[^"\n]*\\([^\\"\n]+\.csv)"\)',r'File.Contents(DataFolder & "\\\1")',expression)
                assert count == 1, table['name']
                expression = expression.replace('Encoding=1252','Encoding=65001').replace('QuoteStyle.None','QuoteStyle.Csv')
                expression = expression.replace('}})', '}}, "en-US")')
                source['expression'] = expression.split('\n')
                queries.append('// Query: '+table['name']+'\n'+expression)
            for measure in table.get('measures',[]):
                if measure['name'] == 'Churn Rate':
                    measure['formatString'] = '0.00%'
                elif measure['name'].startswith('Average'):
                    measure['formatString'] = '#,##0.00'
        # Single filter route: companies -> customers -> survey/usage.
        relationships = []
        for relation in model['relationships']:
            if relation['fromTable'] == 'survey' and relation['toTable'] == 'companies':
                continue
            if relation['fromTable'] == 'survey' and relation['toTable'] == 'customers':
                relation.update(fromCardinality='many',toCardinality='one',isActive=True,crossFilteringBehavior='oneDirection')
            relationships.append(relation)
        model['relationships'] = relationships
        (out/'DataModelSchema.json').write_text(json.dumps(schema,indent=2),encoding='utf-8')
        (out/'queries.pq').write_text('// Create DataFolder as a required Text parameter first.\n\n'+'\n\n'.join(queries),encoding='utf-8')
        layout = original.read('Report/Layout')
        candidate = out/'Visuals_repaired_CANDIDATE.pbit'
        with zipfile.ZipFile(candidate,'w',zipfile.ZIP_DEFLATED) as repaired:
            for item in original.infolist():
                if item.filename == 'SecurityBindings':
                    continue  # stale binding from the original package
                content = original.read(item.filename)
                if item.filename == 'DataModelSchema':
                    content = json.dumps(schema,ensure_ascii=False).encode('utf-16-le')
                elif item.filename == '[Content_Types].xml':
                    xml = ET.fromstring(content)
                    for child in list(xml):
                        if 'SecurityBindings' in child.attrib.get('PartName',''):
                            xml.remove(child)
                    content = ET.tostring(xml,encoding='utf-8',xml_declaration=True)
                repaired.writestr(item,content)
    with zipfile.ZipFile(candidate) as z:
        assert z.testzip() is None
        assert z.read('Report/Layout') == layout
        parsed = json.loads(z.read('DataModelSchema').decode('utf-16-le'))
        paths = [str(p['source']['expression']) for t in parsed['model']['tables'] for p in t['partitions'] if p['source']['type']=='m']
        assert len(paths)==4 and all('DataFolder' in x and 'OneDrive' not in x for x in paths)
    audit = {'candidate_zip_crc':'passed','schema_json':'passed','parameterized_queries':4,
             'original_report_layout_preserved':True,'desktop_open_refresh_render':'NOT VALIDATED',
             'pbix_original':'unchanged; embedded data/model not rewritten',
             'report_pages':len(json.loads(layout.decode('utf-16-le'))['sections'])}
    (out/'validation.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(json.dumps(audit,indent=2))

if __name__ == '__main__':
    build()
