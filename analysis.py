"""Reproduce the synthetic coworking case study: python analysis.py."""
from pathlib import Path
import hashlib
import json
import platform
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import sklearn

ROOT = Path(__file__).resolve().parent

def require(condition, message):
    if not condition:
        raise ValueError(message)

def prepare(root=ROOT):
    data = {n: pd.read_csv(root / f'{n}.csv') for n in ['customers', 'companies', 'survey', 'usage_monthly']}
    c, co, s, u = (data[n] for n in ['customers', 'companies', 'survey', 'usage_monthly'])
    required = {
        'customers': 'Customer_ID Company Join_Date Exit_Date Monthly_Spend Location Team_Size Churned',
        'companies': 'Company Base_Monthly_Price Private_Office Hot_Desk Conference_Hours Free_Coffee Internet_Speed_Mbps Flexibility_Score',
        'survey': 'Customer_ID Company Survey_Date Satisfaction_Score Amenity_Rating Price_Rating NPS_Like',
        'usage_monthly': 'Customer_ID Company Month Days_Used Meeting_Hours Support_Tickets Monthly_Revenue'}
    for name, frame in data.items():
        require(list(frame.columns) == required[name].split(), f'{name}: unexpected schema')
        require(not frame.duplicated().any(), f'{name}: duplicate full rows')
    require(c.Customer_ID.is_unique and co.Company.is_unique, 'Duplicate dimension keys')
    for frame in [c.drop(columns='Exit_Date'), co, s]:
        require(not frame.isna().any().any(), 'Missing required dimension/survey fields')
    for frame, columns in [(c, ['Join_Date','Exit_Date']), (s,['Survey_Date']), (u,['Month'])]:
        for col in columns:
            frame[col] = pd.to_datetime(frame[col], format='%Y-%m-%d', errors='raise')
    incomplete = u.isna().any(axis=1)
    rejected = u.loc[incomplete].copy()
    rejected['Source_Line'] = rejected.index + 2
    rejected['Reason'] = 'Missing required field(s); values not inferred'
    u = u.loc[~incomplete].copy()
    data['usage_monthly'] = u
    require(c.Churned.isin([0,1]).all(), 'Invalid churn flag')
    require((c.Churned.eq(1) == c.Exit_Date.notna()).all(), 'Exit/churn mismatch')
    require((c.Exit_Date.isna() | c.Exit_Date.ge(c.Join_Date)).all(), 'Exit before join')
    require(c.Monthly_Spend.gt(0).all() and c.Team_Size.ge(1).all(), 'Invalid spend/team size')
    require(c.Company.isin(co.Company).all(), 'Unknown customer company')
    require(not u.assign(period=u.Month.dt.to_period('M')).duplicated(['Customer_ID','period']).any(), 'Duplicate customer-month')
    require(not s.duplicated(['Customer_ID','Survey_Date']).any(), 'Duplicate survey key')
    flags = []
    after_exit = 0
    for name, frame, date in [('usage_monthly',u,'Month'), ('survey',s,'Survey_Date')]:
        joined = frame.merge(c[['Customer_ID','Company','Join_Date','Exit_Date']], on='Customer_ID', how='left', suffixes=('','_customer'), validate='many_to_one', indicator=True)
        require(joined['_merge'].eq('both').all(), f'{name}: orphan customer')
        require(joined.Company.eq(joined.Company_customer).all(), f'{name}: company mismatch')
        require(joined[date].ge(joined.Join_Date).all(), f'{name}: event before join')
        late = joined.Exit_Date.notna() & joined[date].gt(joined.Exit_Date)
        if name == 'usage_monthly':
            require(not late.any(), 'Usage after exit')
        else:
            after_exit = int(late.sum())
            f = joined.loc[late,['Customer_ID',date,'Exit_Date']].copy()
            f['Reason'] = 'Survey after exit; retained for descriptive analysis only'
            flags.append(f)
    for col in ['Satisfaction_Score','Amenity_Rating','Price_Rating']:
        require(s[col].between(1,10).all(), f'Invalid {col}')
    require(u.Days_Used.between(0,31).all(), 'Invalid usage days')
    require(u[['Meeting_Hours','Support_Tickets','Monthly_Revenue']].ge(0).all().all(), 'Negative usage measure')
    extreme = c.Team_Size.gt(100)  # review threshold, not an assertion of invalidity
    f = c.loc[extreme,['Customer_ID','Team_Size']].copy()
    f['Reason'] = 'Team size >100: review threshold; original retained'
    flags.append(f)
    audit = {'source_rows': {n: int(len(pd.read_csv(root/f'{n}.csv'))) for n in data},
             'prepared_rows': {n:len(d) for n,d in data.items()},
             'usage_quarantined':len(rejected), 'surveys_after_exit':after_exit,
             'team_size_over_100':int(extreme.sum()),
             'date_ranges':{n:{col:[str(d[col].min().date()),str(d[col].max().date())] for col in d.select_dtypes('datetime').columns} for n,d in data.items()},
             'source_sha256':{n:hashlib.sha256((root/f'{n}.csv').read_bytes()).hexdigest() for n in data}}
    return data, rejected, pd.concat(flags,ignore_index=True), audit

def benchmark(c):
    # No exit date, churn-derived tenure, ID, usage, or survey features.
    features = ['Company','Location','Monthly_Spend','Team_Size']
    train, test = train_test_split(c.index, test_size=.25, stratify=c.Churned, random_state=42)
    transform = ColumnTransformer([
        ('category',OneHotEncoder(handle_unknown='ignore'),['Company','Location']),
        ('numeric',make_pipeline(SimpleImputer(strategy='median'),StandardScaler()),['Monthly_Spend','Team_Size'])])
    models = {'majority_baseline':DummyClassifier(strategy='prior'),
              'logistic_regression':make_pipeline(transform,LogisticRegression(max_iter=2000,random_state=42))}
    rows = []
    predictions = c.loc[test,['Customer_ID','Churned']].copy()
    for name, model in models.items():
        model.fit(c.loc[train,features],c.loc[train,'Churned'])
        probability = model.predict_proba(c.loc[test,features])[:,1]
        predicted = (probability >= .5).astype(int)
        y = c.loc[test,'Churned']
        rows.append({'model':name,'test_customers':len(test),'test_churn_rate':float(y.mean()),
            'roc_auc':roc_auc_score(y,probability),'average_precision':average_precision_score(y,probability),
            'accuracy':accuracy_score(y,predicted),'precision_at_0_5':precision_score(y,predicted,zero_division=0),
            'recall_at_0_5':recall_score(y,predicted,zero_division=0),'f1_at_0_5':f1_score(y,predicted,zero_division=0),
            'confusion_matrix':confusion_matrix(y,predicted).tolist()})
        predictions[name+'_probability'] = probability
    predictions['split'] = 'test'
    return rows,predictions

def run(root=ROOT):
    data,rejected,flags,audit = prepare(root)
    out = root/'reports'
    prepared = root/'data'/'prepared'
    out.mkdir(exist_ok=True)
    prepared.mkdir(parents=True,exist_ok=True)
    for name,frame in data.items():
        frame.to_csv(prepared/f'{name}.csv',index=False,date_format='%Y-%m-%d')
    rejected.to_csv(out/'quarantined_usage.csv',index=False)
    flags.to_csv(out/'review_flags.csv',index=False,date_format='%Y-%m-%d')
    c = data['customers']
    audit['customer_count'] = len(c)
    audit['churned_count'] = int(c.Churned.sum())
    audit['recorded_churn_share'] = float(c.Churned.mean())
    audit['versions'] = {'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'scikit-learn':sklearn.__version__,'matplotlib':matplotlib.__version__}
    for col in ['Company','Location']:
        summary = c.groupby(col).agg(customers=('Customer_ID','size'),churned=('Churned','sum'),churn_share=('Churned','mean'),mean_monthly_spend=('Monthly_Spend','mean'))
        summary.to_csv(out/f'churn_by_{col.lower()}.csv')
    results,predictions = benchmark(c)
    (out/'model_metrics.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    predictions.to_csv(out/'test_predictions.csv',index=False)
    (out/'validation.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax = plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
    c.groupby('Company').Churned.mean().sort_values().plot.barh(ax=ax[0],color='#287d8e')
    ax[0].xaxis.set_major_formatter(PercentFormatter(1))
    ax[0].set(xlabel='Recorded churn share',ylabel='',title='Customer records by provider')
    c.groupby(c.Join_Date.dt.year).size().plot.bar(ax=ax[1],color='#485c80',rot=0)
    ax[1].set(xlabel='Join year',ylabel='Customer records',title='Acquisition history in supplied sample')
    fig.suptitle('Coworking case study | Simulated data',fontweight='bold')
    fig.savefig(out/'overview.png',dpi=160)
    plt.close(fig)
    print(json.dumps({'validation':audit,'benchmark':results},indent=2))
    return data,audit,results

if __name__ == '__main__':
    run()
