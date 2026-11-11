"""Normalize the secondary compilation without upgrading its source certainty."""
from pathlib import Path
import csv,re,json,hashlib,collections,statistics
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'data/raw/download_archive_2026-11-02/compiled_research_package/Bay_Laguna_Research_Datasets_2026'
OUT=ROOT/'data/analysis_ready/compiled_reference_v1';OUT.mkdir(parents=True,exist_ok=True)
def write(name,rows,fields=None):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def snake(s):return re.sub(r'[^a-z0-9]+','_',s.strip().lower()).strip('_')
profiles=[];inventory=[];mapping=[];issues=[]
for p in sorted(SRC.glob('*.csv')):
    with p.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f);headers=reader.fieldnames;raw=list(reader)
    names=[snake(k) for k in headers];assert len(set(names))==len(names)
    rows=[{snake(k):v.strip() for k,v in r.items()} for r in raw]
    for a,b in zip(headers,names):mapping.append({'dataset':p.stem,'original_header':a,'clean_header':b})
    for col in names:
        values=[r[col] for r in rows];nonempty=[v for v in values if v!=''];numeric=bool(nonempty) and all(re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)',v) for v in nonempty)
        dtype='numeric' if numeric else 'character';nums=[float(v) for v in nonempty] if numeric else []
        profiles.append({'dataset':p.stem,'variable':col,'type':dtype,'rows':len(rows),'missing_count':len(values)-len(nonempty),'distinct_nonmissing':len(set(nonempty)),'minimum':min(nums) if nums else '', 'maximum':max(nums) if nums else '', 'example':nonempty[0] if nonempty else ''})
    duplicate_rows=len(rows)-len({tuple(r.values()) for r in rows})
    for i,r in enumerate(rows,2):
        r['source_file']=p.name;r['source_csv_row']=i;r['source_review_status']='secondary_compilation_not_independently_verified'
        if p.stem=='lake_monthly':r['observation_month']=f'{int(r["year"]):04d}-{int(r["month"]):02d}'
        for field in ['onset_or_period_start','period_end','report_date','date','event_date_or_period']:
            if field in r:
                s=r[field];r[field+'_precision']='unavailable' if not s else 'day' if re.fullmatch(r'\d{4}-\d{2}-\d{2}',s) else 'month' if re.fullmatch(r'\d{4}-\d{2}',s) else 'year' if re.fullmatch(r'\d{4}',s) else 'period_or_text_requires_interpretation'
        if p.stem=='fish_kill_events':
            caution=r['counting_or_date_caution'].lower()
            r['estimated_dead_count_qualifier']='lower_bound' if r['estimated_dead_count'] and re.search(r'more than|lower bound|minimum',caution) else 'as_reported_not_revalidated'
            r['model_label_status']='reference_event_only_no_negative_class_created'
        if p.stem=='gate_operating_rules':r['model_label_status']='historical_rule_not_actual_operation'
        if p.stem=='bay_flood_history' and re.search(r'conflict|carina',r['confidence_and_conflicts']+' '+r['named_event'],re.I):
            issues.append({'dataset':p.stem,'source_csv_row':i,'issue':'date_or_named_event_conflict','handling':'Original period and caution retained; not merged as a verified dated event'})
    write(p.name,rows)
    inventory.append({'dataset':p.stem,'rows':len(rows),'original_columns':len(headers),'clean_columns':len(rows[0]),'duplicate_full_rows':duplicate_rows,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'readiness':'Structural cleaning complete; source values remain secondary and require task-specific review'})
    assert len(raw)==len(rows)
write('variable_profiles.csv',profiles);write('dataset_inventory.csv',inventory);write('column_name_mapping.csv',mapping)
write('reference_review_queue.csv',issues,['dataset','source_csv_row','issue','handling'])
with (OUT/'lake_monthly.csv').open(encoding='utf-8-sig') as f:monthly=list(csv.DictReader(f))
assert len(monthly)==60 and len({r['observation_month'] for r in monthly})==60
assert all(r['lake_level_mean_m'] for r in monthly)
(OUT/'README.md').write_text('''# Compiled research reference tables

Eleven CSV tables were normalized to snake_case headers and trimmed text. Row counts, missing fields, numeric types, source hashes and duplicate full rows are profiled. Blank values remain blank. No observations were invented or removed. Partial dates retain their precision; no day is invented for month-only events.

These are secondary compiled references, not newly verified primary records. The 60 monthly lake levels are lake-wide aggregates. Nine recorded fish-kill periods do not establish a complete event register or reliable negative examples. Historical gate rules are not operation logs, and their Marikina River thresholds cannot be treated as lake-level thresholds. Original cautions, lower-bound counts, source URLs and date conflicts are retained. Reference tables remain separate from the source-reviewed station BOD/DO dataset.
''',encoding='utf-8')
print(json.dumps({'tables':len(inventory),'rows':sum(r['rows'] for r in inventory),'duplicate_full_rows':sum(r['duplicate_full_rows'] for r in inventory),'reference_issues':len(issues)},indent=2))
