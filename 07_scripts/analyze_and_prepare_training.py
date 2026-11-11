"""Descriptive EDA and explicit, retrospective next-month DO training candidates.
No estimators, imputers, scalers, or fitted model are created here.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tmp/analysis_deps'))
import json,csv,math,hashlib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'data/analysis_ready/llda_lake_bod_do_v1'
TRAIN=ROOT/'data/training_candidates/do_next_month_v1';TRAIN.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'outputs/cleaned_data_analysis';OUT.mkdir(parents=True,exist_ok=True)
CHART=OUT/'charts';CHART.mkdir(exist_ok=True)
df=pd.read_csv(SRC/'lake_measurements_reviewed_long.csv',keep_default_na=False)
df['numeric_value']=pd.to_numeric(df.numeric_value,errors='coerce')
exact=df[df.numeric_value.notna() & df.qualifier.eq('=')].copy()
exact['year']=exact.observation_month.str[:4].astype(int)
exact['month']=exact.observation_month.str[-2:].astype(int)
core=['L_I','L_II','L_IV','L_V','L_VIII','L_XV','L_XVI','L_XVII','L_XVIII']
def save(frame,name):frame.to_csv(OUT/name,index=False,encoding='utf-8-sig')
stats=exact.groupby('parameter').numeric_value.describe(percentiles=[.25,.5,.75]).reset_index().rename(columns={'count':'exact_value_count','50%':'median','25%':'q1','75%':'q3'})
stats['unit']='mg/L';save(stats,'descriptive_statistics.csv')
status=pd.crosstab(df.parameter,df.value_status).reset_index()
status['reviewed_cells']=status.drop(columns='parameter').sum(axis=1)
save(status,'reviewed_value_status_counts.csv')
annual=[]
for scope,part in [('all_listed_stations',exact),('historical_nine_stations',exact[exact.station_id.isin(core)])]:
 for (year,par),g in part.groupby(['year','parameter']):
  annual.append({'scope':scope,'year':year,'parameter':par,'n':len(g),'stations':g.station_id.nunique(),'mean':g.numeric_value.mean(),'median':g.numeric_value.median(),'min':g.numeric_value.min(),'max':g.numeric_value.max(),'fraction_integer_valued':np.isclose(g.numeric_value,g.numeric_value.round()).mean(),'partial_year':year==2026})
annual=pd.DataFrame(annual);save(annual,'annual_statistics.csv')
season=exact[exact.station_id.isin(core)].groupby(['parameter','month']).numeric_value.agg(['count','mean','median','std']).reset_index();save(season,'month_of_year_statistics.csv')
wide=exact.pivot(index=['station_id','observation_month'],columns='parameter',values='numeric_value').reset_index()
matched=wide.dropna(subset=['bod','dissolved_oxygen'])
corr=float(matched.bod.corr(matched.dissolved_oxygen))
save(pd.DataFrame([{'comparison':'BOD and DO in the same station and reported month','n':len(matched),'pearson_r':corr,'interpretation':'Descriptive pooled association only; station/time dependence and reporting changes are not adjusted'}]),'paired_bod_do_correlation.csv')
names=dict(df[['station_id','station_name']].drop_duplicates().values)
lookup={(r.station_id,r.observation_month,r.parameter):(float(r.numeric_value),r.record_id) for r in exact.itertuples()}
def mid(s):y,m=map(int,s.split('-'));return y*12+m-1
def ms(n):return f'{n//12:04d}-{n%12+1:02d}'
rows=[];do_only=[];exclusions=[]
for sid,mo in sorted({(r.station_id,r.observation_month) for r in exact.itertuples() if r.parameter=='dissolved_oxygen'}):
 n=mid(mo);sources=[lookup.get((sid,ms(n+off),'dissolved_oxygen')) for off in [0,-1,-2,1]]
 if not all(sources):
  exclusions.append({'station_id':sid,'origin_month':mo,'reason':'Missing exact DO in one or more required calendar months t-2, t-1, t, t+1'});continue
 target=ms(n+1);m=int(target[-2:]);bod=lookup.get((sid,mo,'bod'))
 split='train' if target<='2022-12' else 'validation' if target<='2023-12' else 'test'
 row={'example_id':hashlib.sha256(f'{sid}/{mo}/do_next_month_v1'.encode()).hexdigest()[:20],'station_id':sid,'origin_month':mo,'target_month':target,'do_t_mg_l':sources[0][0],'do_t_minus_1_mg_l':sources[1][0],'do_t_minus_2_mg_l':sources[2][0],'target_month_sin':math.sin(2*math.pi*m/12),'target_month_cos':math.cos(2*math.pi*m/12),'target_do_next_month_mg_l':sources[3][0],'proposed_split':split,'do_t_record_id':sources[0][1],'do_t_minus_1_record_id':sources[1][1],'do_t_minus_2_record_id':sources[2][1],'target_record_id':sources[3][1]}
 do_only.append(row.copy())
 if bod:row['bod_t_mg_l']=bod[0];row['bod_t_record_id']=bod[1];rows.append(row)
 else:exclusions.append({'station_id':sid,'origin_month':mo,'reason':'DO history and target available, but current BOD is not an exact numeric value'})
training=pd.DataFrame(rows)
features=['station_id','do_t_mg_l','do_t_minus_1_mg_l','do_t_minus_2_mg_l','bod_t_mg_l','target_month_sin','target_month_cos']
target='target_do_next_month_mg_l'
order=['example_id','station_id','origin_month','target_month']+[f for f in features if f!='station_id']+[target,'proposed_split','do_t_record_id','do_t_minus_1_record_id','do_t_minus_2_record_id','bod_t_record_id','target_record_id']
training=training[order].sort_values(['target_month','station_id']).reset_index(drop=True)
seen_stations=set(training.loc[training.proposed_split.eq('train'),'station_id'])
training['station_seen_in_training']=training.station_id.isin(seen_stations)
order.append('station_seen_in_training')
training.to_csv(TRAIN/'training_do_next_month.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(do_only).sort_values(['target_month','station_id']).to_csv(TRAIN/'alternative_do_history_only.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(exclusions).to_csv(TRAIN/'excluded_origins.csv',index=False,encoding='utf-8-sig')
for split in ['train','validation','test']:training[training.proposed_split.eq(split)].to_csv(TRAIN/(split+'.csv'),index=False,encoding='utf-8-sig')
splitstats=training.groupby('proposed_split',sort=False).agg(examples=('example_id','size'),first_target_month=('target_month','min'),last_target_month=('target_month','max'),stations=('station_id','nunique')).reset_index()
splitstats.to_csv(TRAIN/'split_summary.csv',index=False,encoding='utf-8-sig')
assert len(training)==training.example_id.nunique()
assert training[features+[target]].notna().all().all()
assert all(mid(t)-mid(o)==1 for o,t in zip(training.origin_month,training.target_month))
assert set(training.target_record_id).issubset(set(exact.record_id))
assert training.groupby('target_month').proposed_split.nunique().max()==1
assert training[training.proposed_split.eq('train')].target_month.max()<training[training.proposed_split.eq('validation')].target_month.min()
assert training[training.proposed_split.eq('validation')].target_month.max()<training[training.proposed_split.eq('test')].target_month.min()
metadata={'task':'Proposed retrospective one-month-ahead lake dissolved oxygen regression','status':'Candidate experiment, not a replacement for original thesis objectives or a deployed early-warning model','unit':'mg/L','features':features,'categorical_features':['station_id'],'target':target,'metadata_not_features':[c for c in order if c not in features+[target]],'input_window':'Exact DO from t-2, t-1 and t, plus exact BOD at t; target DO at t+1','known_calendar_features':'Sine and cosine of target month number; known without observing the target','split_rule':'By target month: train through 2022-12; validation during 2023; test from 2024-01 through 2026-06. All stations use the same dates. Proposed boundaries are explicit, not tuned using model results.','missing_policy':'Complete cases for selected features and target. No zero filling or imputation. Censored BOD is excluded from the primary candidate. DO-only alternative is supplied separately.','leakage_controls':'Use only listed features. Never use example_id, dates, split labels, record IDs or the target as predictor columns. Fit preprocessing and categorical encoders on training data only. Historical observations across split boundaries are permitted for rolling one-month prediction; target labels stay chronological.','availability_limitation':'Actual sampling and publication timestamps are unknown. Inputs from quarterly published reports may have become available after the target month. This is an observational retrospective candidate until actual input availability is established.','evaluation_note':'Full-period EDA is supplied. The test period is temporally held out for model fitting but has not been hidden from descriptive exploration. Spatial and temporal observations are dependent.','examples':len(training),'do_only_examples':len(do_only),'source_hash':hashlib.sha256((SRC/'lake_measurements_reviewed_long.csv').read_bytes()).hexdigest(),'checks_passed':['unique examples','all selected features and targets populated','calendar-adjacent targets','source IDs resolve to exact reviewed cells','same split for all stations in a month','chronologically ordered target periods'],'model_training':'No model trained'}
metadata['unseen_station_test_examples']=int((training.proposed_split.eq('test') & ~training.station_seen_in_training).sum())
metadata['new_station_policy']='Station XXIV has no training-period observations. Fit encoders on training data, handle unseen categories explicitly, and report known-station and new-station test performance separately. station_seen_in_training is reporting metadata, not an authorized predictor.'
(TRAIN/'feature_schema.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
(TRAIN/'README.md').write_text('''# Next month DO training candidate

Use training_do_next_month.csv as the combined candidate table, or train.csv, validation.csv and test.csv for the proposed chronological split. Read feature_schema.json first: it lists predictor columns, the target and metadata that must not enter the model.

The target is next-month dissolved oxygen in mg/L. Inputs are station identity, exact DO in the current and preceding two months, exact current-month BOD, and the known target month as cyclic calendar features. Every required month is checked against the calendar. Rows with missing or censored required values are excluded without imputation. alternative_do_history_only.csv is a separate candidate for studying whether requiring BOD unnecessarily reduces coverage.

This is a proposed retrospective forecasting dataset. Report publication times are unknown, so timely operational availability of current-month inputs has not been established. It is not a fish-kill classification, carrying-capacity or gate-control training dataset. No model has been trained. Full-period descriptive exploration has been performed; the future test split is not a blind, previously unseen research holdout.
''',encoding='utf-8')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white'})
# Coverage uses status text, not zero imputation.
panel=pd.read_csv(SRC/'lake_station_month_calendar.csv',keep_default_na=False)
statusmap={'reported_numeric':0,'censored':1,'blank_as_reported':2,'missing_as_reported':2,'no_data_as_reported':2,'unreadable_source':3,'source_report_unavailable':4,'station_not_listed_in_reviewed_table':5,'parameter_not_in_reviewed_table':5}
from matplotlib.colors import ListedColormap,BoundaryNorm
cmap=ListedColormap(['#2a7f9e','#e6a23c','#b8c2cc','#c44949','#696d73','#f0f2f4'])
fig,axes=plt.subplots(2,1,figsize=(11.8,7),sharex=True,constrained_layout=True)
months=sorted(panel.observation_month.unique());sids=list(names)
for ax,par,title in zip(axes,['dissolved_oxygen','bod'],['Dissolved oxygen coverage','BOD coverage']):
 grid=panel.pivot(index='station_id',columns='observation_month',values=par+'_status').reindex(index=sids,columns=months)
 vals=grid.map(statusmap.get).to_numpy(dtype=float)
 ax.imshow(vals,aspect='auto',cmap=cmap,norm=BoundaryNorm(np.arange(-.5,6.5),6),interpolation='nearest')
 ax.set_yticks(range(len(sids)),[s.replace('L_','') for s in sids]);ax.set_ylabel('Station code');ax.set_title(title,loc='left',fontweight='bold')
ticks=[i for i,m in enumerate(months) if m.endswith('-01')];axes[-1].set_xticks(ticks,[months[i][:4] for i in ticks]);axes[-1].set_xlabel('Reported observation month')
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=c,label=l) for c,l in zip(cmap.colors,['Exact','Censored','Source missing','Unreadable','Report unavailable','Station or parameter not in reviewed table'])],loc='outside lower center',ncol=3,frameon=False,fontsize=9)
fig.savefig(CHART/'coverage.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(11.8,4.2),constrained_layout=True)
for ax,par,title in zip(axes,['dissolved_oxygen','bod'],['Dissolved oxygen','BOD']):
 v=exact.loc[exact.parameter.eq(par),'numeric_value'];ax.hist(v,bins=25,color='#2a7f9e',edgecolor='white');ax.set_title(title,loc='left',fontweight='bold');ax.set_xlabel('mg/L');ax.set_ylabel('Exact parameter cells')
fig.savefig(CHART/'distributions.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,axes=plt.subplots(2,1,figsize=(11.8,6.5),constrained_layout=True)
south=panel[panel.station_id.eq('L_VIII')].copy();dates=pd.to_datetime(south.observation_month+'-01')
for ax,par,title in zip(axes,['dissolved_oxygen','bod'],['South Bay dissolved oxygen','South Bay BOD']):
 ax.plot(dates,pd.to_numeric(south[par+'_mg_l'],errors='coerce'),color='#2a7f9e',lw=1.25);ax.set_title(title,loc='left',fontweight='bold');ax.set_ylabel('mg/L');ax.grid(axis='y',alpha=.2)
axes[-1].set_xlabel('Reported month; lines break at unavailable values')
fig.savefig(CHART/'south_bay_history.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(11.8,4.2),constrained_layout=True)
a=annual[(annual.scope=='historical_nine_stations')&(annual.parameter=='dissolved_oxygen')]
axes[0].plot(a.year,a['mean'],marker='o',color='#2a7f9e');axes[0].set_title('DO annual mean in the historical nine stations',loc='left',fontsize=10,fontweight='bold');axes[0].set_ylabel('mg/L');axes[0].set_xlabel('2026 covers January to June only')
axes[1].plot(a.year,a.fraction_integer_valued*100,marker='o',color='#b37a28');axes[1].set_title('Share of exact DO values that are whole numbers',loc='left',fontsize=10,fontweight='bold');axes[1].set_ylabel('% of exact DO cells');axes[1].set_ylim(0,105);axes[1].set_xlabel('Observed precision indicator; not instrument metadata')
fig.savefig(CHART/'reporting_patterns.png',dpi=180,bbox_inches='tight');plt.close(fig)
metrics={'stats':stats.to_dict(orient='records'),'status':status.to_dict(orient='records'),'same_month_bod_do_pearson_r':corr,'matched_bod_do_station_months':len(matched),'training_examples':len(training),'do_only_examples':len(do_only),'split_summary':splitstats.to_dict(orient='records'),'annual_core_do':a.to_dict(orient='records'),'do_below_5_cells':int(((exact.parameter=='dissolved_oxygen')&(exact.numeric_value<5)).sum()),'do_below_5_stations':sorted(exact.loc[(exact.parameter=='dissolved_oxygen')&(exact.numeric_value<5),'station_id'].unique().tolist())}
(OUT/'analysis_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
report=f'''# Cleaned lake data analysis

Prepared 2 November 2026. Analysis uses exact source-reviewed lake BOD/DO only. No model was trained. Python was used for this analysis; R execution is still pending.

## Findings

- The release contains 3,384 exact values in 1,766 station-months from 52 quarterly reports. Across the reviewed cells, 24 are censored, 146 are source-missing, and one unreadable digit is excluded.
- Exact DO values have mean {stats.set_index('parameter').loc['dissolved_oxygen','mean']:.2f} mg/L and median {stats.set_index('parameter').loc['dissolved_oxygen','median']:.2f} mg/L. Exact BOD has mean {stats.set_index('parameter').loc['bod','mean']:.2f} mg/L and median {stats.set_index('parameter').loc['bod','median']:.2f} mg/L. These pooled summaries weight available cells and do not estimate a balanced lake-wide average.
- {metrics['do_below_5_cells']} reported DO cells are below 5 mg/L. This is a descriptive threshold count, not a fish-kill label. Monthly observations cannot reveal unobserved daily or hourly oxygen minima.
- Matched same-month BOD and DO have pooled Pearson r = {corr:.3f} across {len(matched):,} station-months. This is not a causal or out-of-sample predictive estimate. Station, time and reporting effects are not adjusted.
- Historical station coverage is longer than coverage at newly listed stations. The nine older station identities appear from 2013; six additional station identities appear in this reviewed series from 2021, and station XXIV from 2025. These are first appearances in the reviewed tables, not independently verified commissioning dates.
- Later reports contain many whole-number DO values. Annual changes may reflect measurement or reporting practice as well as environmental variation. Method and instrument metadata are needed before explaining this shift.
- Missingness has source-documented causes in some periods, including equipment failure, shallow water and weather. Complete-case training can therefore select a nonrepresentative subset; it is not justified to assume missingness is random.

## Candidate training file

training_do_next_month.csv has {len(training):,} complete supervised rows. Target: next-month DO in mg/L. Inputs: station ID, exact DO at t, t-1 and t-2, exact BOD at t, and the known target month as sine/cosine calendar features. Rows never jump across missing months. The DO-only alternative has {len(do_only):,} rows and can support a later coverage sensitivity comparison.

Proposed splits use target month, shared by all stations: train through December 2022, validation in 2023, and test from January 2024 through June 2026. Fit encoders and preprocessing on training data only. Earlier observations may be used across boundaries in a rolling forecast; future target labels may not be used as inputs. Full-period EDA has already been performed, so the proposed test period is not a blind research holdout.

Station XXIV appears only in the proposed test period. Its {metadata['unseen_station_test_examples']} test examples require explicit handling of an unseen categorical station ID. Fit encoders on training data and report new-station performance separately from performance at known stations.

Current-month BOD/DO from a quarterly publication may not have been available before next month's target. Publication and actual sample timestamps are unknown. This candidate supports a retrospective observational experiment until timely operational input availability is established. It does not supply fish-kill, capacity or gate-control labels.

## Files

Descriptive CSVs and charts are in this analysis folder. Reviewed source data are under data/analysis_ready/llda_lake_bod_do_v1. Candidate training tables and feature_schema.json are under data/training_candidates/do_next_month_v1. Source locators, missing categories and correction logs are preserved in the reviewed release.
'''
(OUT/'ANALYSIS_REPORT.md').write_text(report,encoding='utf-8')
print(json.dumps(metrics,indent=2))
