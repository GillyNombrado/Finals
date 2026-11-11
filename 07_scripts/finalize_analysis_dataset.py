"""Release a source-reviewed lake BOD/DO panel; quarantine the broader OCR archive.

The explicit transcription file is the review authority. This script never
promotes OCR confidence into evidence of numerical correctness.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv, json, re, hashlib, calendar, statistics, shutil
from clean_reports import LAKE, value
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/analysis_ready/llda_lake_bod_do_v1'
OUT.mkdir(parents=True,exist_ok=True)
OLD=ROOT/'data/clean/llda_2026-11-02'
MANIFEST=json.loads((ROOT/'scripts/data_preparation/reviewed_lake_sources.json').read_text(encoding='utf-8'))
SOURCES={f'{r["year"]}q{r["quarter"]}':r for r in MANIFEST}
def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows,fields=None):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),extrasaction='ignore');w.writeheader();w.writerows(rows)
def mid(s):
    y,m=map(int,s.split('-'));return y*12+m-1
def mstr(n):return f'{n//12:04d}-{n%12+1:02d}'
def longest(months):
    nums=sorted({mid(m) for m in months});best=run=0;last=None
    for n in nums:
        run=run+1 if last is not None and n==last+1 else 1;best=max(best,run);last=n
    return best
blocks={};key=None
for line in (ROOT/'scripts/data_preparation/reviewed_lake_bod_do.txt').read_text(encoding='utf-8').splitlines():
    line=line.strip()
    if not line or line.startswith('#'):continue
    if re.fullmatch(r'20\d\dq[1-4]',line):
        assert line not in blocks,line
        key=line;blocks[key]=[]
    else:
        cells=line.split();assert len(cells)==7,(key,line)
        blocks[key].append(cells)
assert set(blocks)==set(SOURCES),(set(SOURCES)-set(blocks))
old=read(OLD/'measurements_all.csv');oldkeys=defaultdict(list)
for r in old:oldkeys[(r['source_file'],r['station_id'],r['observation_month'],r['parameter'])].append(r)
records=[];audit=[];scope=[];corrections=[]
for key,items in sorted(blocks.items()):
    src=SOURCES[key];year=src['year'];q=src['quarter']
    assert len({r[0] for r in items})==len(items)
    for rank,item in enumerate(items,1):
        roman=item[0];name=next(n for r,n,_ in LAKE if r==roman)
        for par,start in [('bod',1),('dissolved_oxygen',4)]:
            for off,raw in enumerate(item[start:start+3]):
                month=f'{year}-{q*3-2+off:02d}'
                if raw=='NA':
                    scope.append({'source_file':src['source_file'],'source_page':src['source_page'],'station_id':'L_'+roman,'observation_month':month,'parameter':par,'disposition':'parameter_not_in_reviewed_table','reason':'No BOD column in the reviewed lake table; not evidence that no other source contains BOD.'});continue
                num,op,bound,status,flags=value(raw)
                reason=''
                if raw=='_':num=bound=None;op='';status='blank_as_reported'
                if raw=='ND':num=bound=None;op='';status='no_data_as_reported';reason='Gray cells defined as no data by the source legend'
                if raw=='?':num=bound=None;op='';status='unreadable_source';reason='Source digit not confidently readable; excluded rather than guessed'
                if key=='2021q3' and par=='bod' and off==2:reason='Source note: incubator breakdown in September'
                if key=='2021q3' and roman=='XVII' and off==1:reason='Source note: no sample at XVII in August due to strong winds and waves'
                if key=='2020q4' and par=='bod' and off==1:reason='Source note: no analysis due to Typhoon Ulysses'
                if key=='2024q2' and raw=='*':reason='Source note: no sample due to shallow water'
                rid=hashlib.sha256(f'lake_review_v1/{key}/{roman}/{par}/{off}'.encode()).hexdigest()[:20]
                rec={'record_id':rid,'station_id':'L_'+roman,'station_name':name,'waterbody_type':'lake','observation_month':month,'date_precision':'month','parameter':par,'unit':'mg/L','raw_value':'' if raw=='_' else raw,'numeric_value':num,'qualifier':op,'censoring_bound':bound,'value_status':status,'missing_or_review_reason':reason,'source_file':src['source_file'],'source_page':src['source_page'],'source_table':'Laguna Lake BOD and DO table','source_data_row':rank,'source_month_column':calendar.month_abbr[q*3-2+off],'review_status':'unreadable_source_excluded' if raw=='?' else 'source_visually_checked','verification_date':'2026-11-02','sample_datetime':'','available_at':'','numeric_analysis_eligible':num is not None and op=='='}
                records.append(rec)
                prior=oldkeys.get((src['source_file'],'L_'+roman,month,par),[])
                previous=' | '.join(r['raw_value'] for r in prior)
                priornums=[float(r['numeric_value']) for r in prior if r['numeric_value']]
                action='confirmed' if len(prior)==1 and ((num is not None and priornums==[num] and prior[0]['qualifier']==op) or (prior[0]['raw_value']==rec['raw_value'] and prior[0]['value_status']==status)) else 'corrected_or_recovered'
                corrections.append({'record_id':rid,'source_file':src['source_file'],'source_page':src['source_page'],'station_id':'L_'+roman,'observation_month':month,'parameter':par,'previous_extracted_tokens':previous,'verified_raw_value':rec['raw_value'],'verified_numeric_value':num,'action':action,'review_basis':'Visual source table reading; original extraction retained in earlier release'})
    rs=[r for r in records if r['source_file']==src['source_file']]
    audit.append({'source_file':src['source_file'],'year':year,'quarter':q,'source_page':src['source_page'],'listed_lake_stations':len(items),'reviewed_parameter_cells':len(rs),'exact_numeric_cells':sum(r['numeric_analysis_eligible'] for r in rs),'censored_cells':sum(r['value_status']=='censored' for r in rs),'unreadable_cells':sum(r['value_status']=='unreadable_source' for r in rs),'scope':'Lake DO and BOD where columns present; other parameters and tributaries excluded from this release'})
records.sort(key=lambda r:(r['observation_month'],r['station_id'],r['parameter']))
assert len({(r['station_id'],r['observation_month'],r['parameter']) for r in records})==len(records)
exact=[r for r in records if r['numeric_analysis_eligible']]
assert all(r['numeric_value']>=0 for r in exact)
assert all(0<=r['numeric_value']<=30 for r in exact if r['parameter']=='dissolved_oxygen')
write('lake_measurements_reviewed_long.csv',records)
write('lake_numeric_analysis.csv',exact)
write('source_review_audit.csv',audit)
write('source_review_corrections.csv',corrections)
write('scope_exclusions.csv',scope)
write('non_exact_values.csv',[r for r in records if not r['numeric_analysis_eligible']])
write('unreadable_source_queue.csv',[r for r in records if r['value_status']=='unreadable_source'],list(records[0]))
lookup={(r['station_id'],r['observation_month'],r['parameter']):r for r in records}
panel=[];coverage=[]
for roman,name,_ in LAKE:
    sid='L_'+roman
    for n in range(mid('2013-01'),mid('2026-06')+1):
        mo=mstr(n);yr=int(mo[:4]);q=(int(mo[-2:])-1)//3+1;key=f'{yr}q{q}';src=SOURCES.get(key)
        row={'station_id':sid,'station_name':name,'observation_month':mo,'source_report_status':'available' if src else 'source_report_unavailable','source_file':src['source_file'] if src else '','source_page':src['source_page'] if src else ''}
        for par in ['bod','dissolved_oxygen']:
            r=lookup.get((sid,mo,par));row[par+'_mg_l']=r['numeric_value'] if r else None
            row[par+'_status']=r['value_status'] if r else 'source_report_unavailable' if not src else 'parameter_not_in_reviewed_table' if any(e['source_file']==src['source_file'] and e['station_id']==sid and e['parameter']==par for e in scope) else 'station_not_listed_in_reviewed_table'
            row[par+'_qualifier']=r['qualifier'] if r else ''
            row[par+'_bound_mg_l']=r['censoring_bound'] if r else None
            row[par+'_record_id']=r['record_id'] if r else ''
        panel.append(row)
    for par in ['bod','dissolved_oxygen']:
        rs=[r for r in records if r['station_id']==sid and r['parameter']==par];good=[r for r in rs if r['numeric_analysis_eligible']];vals=[r['numeric_value'] for r in good];months=[r['observation_month'] for r in good]
        coverage.append({'station_id':sid,'station_name':name,'parameter':par,'reviewed_cells':len(rs),'exact_numeric_cells':len(good),'first_numeric_month':min(months) if months else '', 'last_numeric_month':max(months) if months else '', 'longest_consecutive_numeric_months':longest(months),'censored_cells':sum(r['value_status']=='censored' for r in rs),'missing_cells':sum(r['value_status'] in ['blank_as_reported','no_data_as_reported','missing_as_reported'] for r in rs),'unreadable_cells':sum(r['value_status']=='unreadable_source' for r in rs),'minimum':min(vals) if vals else None,'maximum':max(vals) if vals else None,'mean':statistics.mean(vals) if vals else None})
write('lake_station_month_calendar.csv',panel)
write('station_parameter_coverage.csv',coverage)
# Feasibility counts only: adjacent months are checked explicitly, never row-shifted across gaps.
pairs=[]
for r in exact:
    if r['parameter']!='dissolved_oxygen':continue
    nxt=lookup.get((r['station_id'],mstr(mid(r['observation_month'])+1),'dissolved_oxygen'))
    if nxt and nxt['numeric_analysis_eligible']:
        pairs.append({'station_id':r['station_id'],'input_month':r['observation_month'],'target_month':nxt['observation_month'],'current_do_mg_l':r['numeric_value'],'next_month_do_mg_l':nxt['numeric_value'],'input_record_id':r['record_id'],'target_record_id':nxt['record_id'],'purpose':'Feasibility candidate only; forecasting task and release timing not established'})
write('candidate_adjacent_month_do_pairs.csv',pairs)
# Explicit disposition for every earlier OCR-ledger record; quarantining is not deletion.
dispositions=[]
for r in old:
    k=(r['station_id'],r['observation_month'],r['parameter']);new=lookup.get(k)
    if new and new['source_file']==r['source_file']:
        disposition='superseded_by_source_review';why=new['record_id']
    else:disposition='excluded_from_analysis_release';why='Outside reviewed lake BOD/DO scope; original value retained for later review'
    dispositions.append({'previous_record_id':r['record_id'],'source_file':r['source_file'],'station_id':r['station_id'],'observation_month':r['observation_month'],'parameter':r['parameter'],'disposition':disposition,'reason_or_replacement_id':why})
write('prior_extraction_dispositions.csv',dispositions)
summary={'release':'llda_lake_bod_do_v1','reviewed_reports':len(audit),'stations':len(LAKE),'period_start':'2013-01','period_end':'2026-06','reviewed_cells':len(records),'exact_numeric_cells':len(exact),'censored_cells':sum(r['value_status']=='censored' for r in records),'missing_cells':sum(r['value_status'] in ['blank_as_reported','no_data_as_reported','missing_as_reported'] for r in records),'unreadable_cells':sum(r['value_status']=='unreadable_source' for r in records),'numeric_station_month_rows':len({(r['station_id'],r['observation_month']) for r in exact}),'candidate_adjacent_do_pairs':len(pairs),'corrected_or_recovered_cells':sum(r['action']=='corrected_or_recovered' for r in corrections),'status_counts':dict(Counter(r['value_status'] for r in records)),'scope':'Lake BOD/DO only. Broader archive is not fully visually validated.','training_status':'Clean inputs available for exploratory monthly forecasting experiments; thesis target, availability timing, splits and leakage controls must be specified before training.'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
shutil.copy2(ROOT/'scripts/data_preparation/reviewed_lake_bod_do.txt',OUT/'review_transcription.txt')
shutil.copy2(ROOT/'scripts/data_preparation/reviewed_lake_sources.json',OUT/'review_image_manifest.json')
print(json.dumps(summary,indent=2))
